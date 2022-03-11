from functools import partial
import sqlite3 as sql
from tqdm import tqdm
import fpl_api_handler as fpl
from multiprocessing import Pool
class DBHandler():
    """
    Class with methods to create a database and perform operations on it exclusively related to FPL API
    """

    # TO-DO:
    # - Add method/script for team updates
    # - Add method/script for archiving player data at end of season (need for stats analysis)
    # - Add method/script for deleting old data
    
    def __init__(self, db_name = "data/FPL_DB.db"):
        self.db_name = db_name
        self.conn = sql.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_default_tables()
        self.static_inserts()

    def create_default_tables(self):
        with open("src/data-extraction/create_tables.sql", "r") as f:
            self.cursor.executescript(f.read())
        
        self.conn.commit()
    
    def get_table_columns(self, table_name):
        """
        Returns a list of all columns in a table
        """

        self.cursor.execute(f"PRAGMA table_info({table_name})")
        return [row[1] for row in self.cursor.fetchall()]

    def get_update_and_insert_query(self, table_name, pk):
        """
        Returns a query string to update or insert rows in a table
        """

        columns = self.get_table_columns(table_name)
        insert_query = f"INSERT INTO {table_name} VALUES (:{', :'.join(columns)})"
        for key in pk:
            columns.remove(key)
        update_query = f"UPDATE {table_name} SET " + ", ".join([f"{column} = :{column}" for column in columns]) + \
                      " WHERE "+ " AND ".join([f"{k} = :{k}" for k in pk])

        return insert_query, update_query

    def static_inserts(self):
        """
        Inserts static data into the database - data that is not updated every week
        """

        teams_static = fpl.get_static_data("teams")
        positions_static = fpl.get_static_data("element_types")
        metric_names_static = fpl.get_static_data("element_stats")

        with self.conn:
            try:
                self.conn.executemany("INSERT INTO teams_static VALUES (:id, :name, :code, :short_name)", teams_static)
                self.conn.executemany("INSERT INTO positions_static VALUES (:id, :singular_name_short, :squad_max_play, :squad_min_play)", positions_static)
                self.conn.executemany("INSERT INTO metric_names_static VALUES (:name, :label)", metric_names_static)
            except sql.IntegrityError:
                print("Static data already inserted")
    
    def update_events(self):
        """
        Inserts/updates events into the events_static table at a fixed frequency during the season
        """
        insert_query, update_query = self.get_update_and_insert_query("events_static", ["id"])
        try:
            events = fpl.get_static_data("events")
            self.cursor.execute("SELECT COUNT(*) FROM events_static")
            # If zero records insert all events else only current and previous (need to make this failure proof)
            if self.cursor.fetchone()[0] == 0:
                pass
            else:
                events = [e for e in events if e["is_current"] == 1 or e["is_previous"] == 1]

            for event in events:
                event["top_element_info_id"] = event["top_element_info"]["id"]
                event["top_element_info_points"] = event["top_element_info"]["points"]
                event.pop("top_element_info")

        except IndexError:
            print("No current events")
            return

        with self.conn:
            try:
                self.conn.executemany(insert_query, events)
            except sql.IntegrityError:
                print("Events already inserted, performing update")
                self.conn.rollback()
                self.conn.executemany(update_query, events)

    def update_fixtures(self):
        """
        Inserts/updates fixtures into the fixtures table at a fixed frequency during the season
        """
        #Need to check behaviour of API to see if the update works, table should contain only 380 fixtures
        #Else might be wiser to repopulate this table from scratch
        try:
            fixtures = fpl.get_fixtures()
        except IndexError:
            print("No fixtures")
            return
        
        insert_query, update_query = self.get_update_and_insert_query("fixtures", ["id"])

        with self.conn:
            try:
                self.conn.executemany(insert_query, fixtures)
            except sql.IntegrityError:
                print("Fixtures already inserted, performing update")
                self.conn.rollback()
                self.conn.executemany(update_query, fixtures)

    def update_player_static(self):
        """
        Inserts/updates players into the players_static table at a fixed frequency during the season
        """
        try:
            players = fpl.get_static_data("elements")
        except IndexError:
            print("No players")
            return
        
        insert_query, update_query = self.get_update_and_insert_query("players_static", ["id"])

        with self.conn:
            try:
                self.conn.executemany(insert_query, players)
            
            except sql.IntegrityError:
                print("Players already inserted, performing update")
                self.conn.rollback()
                self.conn.executemany(update_query, players)
    
    def update_player_gw_detailed(self):
        """
        Updates player_gw_detailed table with player data for each gameweek
        """

        self.cursor.execute("SELECT MAX(id) from events_static WHERE is_current = 1")
        current_gw = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM player_gw_detailed")
        table_records = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT id FROM players_static")
        
        players = self.cursor.fetchall()
        players = [p[0] for p in players]

        insert_query, update_query = self.get_update_and_insert_query("player_gw_detailed", ["element", "round", "fixture"])

        history = []
        with Pool(8) as p:
            with tqdm(total=len(players)) as pbar:
                for i, data in enumerate(p.imap(partial(fpl.get_player_info, key="history"), players)) :
                    history.append(data)
                    pbar.update()

        if table_records == 0:
            with self.conn:
                for player in history:
                    try:
                        self.conn.executemany(insert_query, player)
                    except:
                        print("Error inserting player", player[0]["element"])
                        raise Exception
        else:
            #Inserting only current gw records
            history = [gw for player in history for gw in player if gw["round"] == current_gw]
            with self.conn:
                try:
                    self.conn.executemany(insert_query, history)
                except sql.IntegrityError:
                    #Update existing records, if already inserted
                    self.conn.executemany(update_query, history)
                except:
                    raise Exception
            

if __name__ == "__main__":
    db = DBHandler()
    db.update_events()
    db.update_fixtures()
    db.update_player_static()
    db.update_player_gw_detailed()
    db.conn.close()
