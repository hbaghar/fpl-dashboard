import sqlite3 as sql
from tqdm import tqdm
import fpl_api_handler as fpl
class DBHandler():
    """
    Class with methods to create a database and perform operations on it exclusively related to FPL API
    """
    
    def __init__(self, db_name = "data/FPL_DB.db"):
        self.db_name = db_name
        self.conn = sql.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.create_default_tables()
        self.static_inserts()

    def create_default_tables(self):
        q = """  
        CREATE TABLE IF NOT EXISTS teams_static (id INTEGER PRIMARY KEY, name TEXT, code INTEGER, short_name TEXT);
        CREATE TABLE IF NOT EXISTS positions_static (id INTEGER PRIMARY KEY, singular_name_short TEXT, squad_max_play INTEGER, squad_min_play INTEGER);
        CREATE TABLE IF NOT EXISTS players_static (id INTEGER PRIMARY KEY, first_name TEXT, second_name TEXT, web_name TEXT, team INTEGER, element_type INTEGER, 
                                                assists INTEGER, bonus INTEGER, bps INTEGER, chance_of_playing_next_round INTEGER, chance_of_playing_this_round INTEGER,
                                                clean_sheets INTEGER, code INTEGER, corners_and_indirect_freekicks_order INTEGER, corners_and_indirect_freekicks_text TEXT,
                                                cost_change_event INTEGER, cost_change_start INTEGER, creativity DOUBLE, creativity_rank INTEGER, creativity_rank_type INTEGER,
                                                direct_freekicks_order INTEGER, direct_freekicks_text TEXT, dreamteam_count INTEGER,
                                                ep_next DOUBLE, event_points INTEGER, form DOUBLE , goals_conceded INTEGER, goals_scored INTEGER,
                                                ict_index DOUBLE, ict_index_rank INTEGER, ict_index_rank_type INTEGER,
                                                influence DOUBLE, influence_rank INTEGER, influence_rank_type INTEGER, minutes INTEGER,
                                                news TEXT, news_added TEXT, now_cost INTEGER, own_goals INTEGER,
                                                penalties_missed INTEGER, penalties_order INTEGER, penalties_saved INTEGER, penalties_text TEXT, photo TEXT,
                                                points_per_game INTEGER, red_cards INTEGER, saves INTEGER, selected_by_percent DOUBLE, 
                                                threat DOUBLE, threat_rank INTEGER, threat_rank_type INTEGER, total_points INTEGER,
                                                value_form DOUBLE, value_season DOUBLE, yellow_cards INTEGER,
                                                FOREIGN KEY(team) REFERENCES teams(id), FOREIGN KEY(element_type) REFERENCES positions(id));
        
        CREATE TABLE IF NOT EXISTS metric_names_static (name TEXT PRIMARY KEY, label TEXT);
        
        CREATE TABLE IF NOT EXISTS events_static (id INTEGER PRIMARY KEY, average_entry_score INTEGER, data_checked TEXT, deadline_time TEXT, finished TEXT, highest_score INTEGER, 
                                                    is_current TEXT, is_next TEXT, is_previous TEXT, most_captained INTEGER, most_selected INTEGER, 
                                                    most_transferred_in INTEGER, most_vice_captained INTEGER,
                                                    name TEXT, top_element INTEGER, top_element_info_id INTEGER, top_element_info_points INTEGER, transfers_made INTEGER);
        
        CREATE TABLE IF NOT EXISTS fixtures (id INTEGER PRIMARY KEY, event INTEGER, team_a INTEGER, team_h INTEGER, team_a_difficulty INTEGER, team_h_difficulty INTEGER);
        
        CREATE TABLE IF NOT EXISTS player_gw_detailed (element INTEGER, assists INTEGER, bonus INTEGER, bps INTEGER, clean_sheets INTEGER, creativity DOUBLE, fixture INTEGER, 
                                                        goals_conceded INTEGER, goals_scored INTEGER, ict_index DOUBLE, influence DOUBLE, kickoff_time TEXT, 
                                                        minutes INTEGER, opponent_team INTEGER, own_goals INTEGER, penalties_missed INTEGER, penalties_saved INTEGER, 
                                                        red_cards INTEGER, round INTEGER, saves INTEGER, selected INTEGER, team_a_score INTEGER, 
                                                        team_h_score INTEGER, threat DOUBLE, total_points INTEGER, transfers_balance INTEGER, transfers_in INTEGER, 
                                                        transfers_out INTEGER, value INTEGER, was_home TEXT, yellow_cards INTEGER,
                                                        CONSTRAINT player_week_fixture PRIMARY KEY (element, round, fixture), FOREIGN KEY(element) REFERENCES players(id), FOREIGN KEY(fixture) REFERENCES fixtures(id));"""
        
        self.cursor.executescript(q)
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
        Excepttion added for: teams_static table, it will be updated once a season
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
                self.conn.rollback()
                self.conn.executemany("UPDATE teams_static SET name = :name, code = :code, short_name = :short_name WHERE id = :id", teams_static)
    
    def update_events(self):
        """
        Inserts/updates events into the events_static table at a fixed frequency during the season
        """
        insert_query, update_query = self.get_update_and_insert_query("events_static", ["id"])
        try:
            # TO-DO: if table is empty, insert all events
            events = fpl.get_static_data("events")
            self.cursor.execute("SELECT COUNT(*) FROM events_static")
            if self.cursor.fetchone()[0] == 0:
                pass
            else:
                events = [e for e in events if e["is_current"] == 1]

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
                print("Event already inserted, performing update")
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
        
        self.cursor.execute("SELECT id from events_static WHERE is_current = 1")
        current_gw = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM player_gw_detailed")
        table_records = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT id FROM players_static")
        
        for player in tqdm(self.cursor.fetchall()):
            history = fpl.get_player_info(player[0], "history")
            insert_query, update_query = self.get_update_and_insert_query("player_gw_detailed", ["element", "round", "fixture"])
            if table_records == 0:
                with self.conn:
                    try:
                        self.conn.executemany(insert_query, history)
                    except:
                        print("Player id: ", player[0])
                        raise Exception
            else:
                #Performing update for latest gw if player has already been inserted
                history = [h for h in history if h["round"] == current_gw]
                with self.conn:
                    try:
                        self.conn.executemany(insert_query, history)
                    except sql.IntegrityError:
                        self.conn.executemany(update_query, history)
                    except:
                        print("Player id: ", player[0])
                        raise Exception
            

if __name__ == "__main__":
    db = DBHandler()
    db.update_events()
    db.update_fixtures()
    db.update_player_static()
    db.update_player_gw_detailed()
    db.conn.close()
