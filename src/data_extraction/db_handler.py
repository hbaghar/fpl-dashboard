from functools import partial
import sqlite3 as sql
from tqdm import tqdm
import src.data_extraction.fpl_api_handler as fpl
from multiprocessing import Pool
import os


class DBHandler:
    """
    Class with methods to create a database and perform operations on it
    """

    def __init__(self, db_name="../data/FPL_DB.db"):
        self.db_name = db_name
        self.conn = sql.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def create_default_tables(self):
        with open("data_extraction/queries/create_tables.sql", "r") as f:
            self.cursor.executescript(f.read())

    def get_table_columns(self, table_name):
        """
        Returns a list of all columns in a table
        """

        self.cursor.execute(f"PRAGMA table_info({table_name})")
        return [row[1] for row in self.cursor.fetchall()]

    def get_unique_values_in_table_column(self, table_name, column_name):
        """
        Returns a list of all values in a column in a table
        """

        self.cursor.execute(f"SELECT DISTINCT {column_name} FROM {table_name}")
        return [row[0] for row in self.cursor.fetchall()]

    def get_insert_query(self, table_name):
        """
        Returns a query string to update or insert rows in a table
        """

        columns = self.get_table_columns(table_name)
        insert_query = f"INSERT INTO {table_name} VALUES (:{', :'.join(columns)})"

        return insert_query

    def static_inserts(self):
        """
        Inserts static data into the database - data that is not updated every week
        """

        teams_static = fpl.get_static_data("teams")
        positions_static = fpl.get_static_data("element_types")
        metric_names_static = fpl.get_static_data("element_stats")

        with self.conn:
            self.conn.executemany(
                "INSERT INTO teams_static VALUES (:id, :name, :code, :short_name)",
                teams_static,
            )
            self.conn.executemany(
                "INSERT INTO positions_static VALUES (:id, :singular_name_short, :squad_max_play, :squad_min_play)",
                positions_static,
            )
            self.conn.executemany(
                "INSERT INTO metric_names_static VALUES (:name, :label)",
                metric_names_static,
            )

    def create_events(self):
        """
        Inserts events into the events_static table
        """
        print("Fetching Events table...")
        insert_query = self.get_insert_query("events_static")
        try:
            events = fpl.get_static_data("events")

            for event in events:
                try:
                    event["top_element_info_id"] = event["top_element_info"]["id"]
                    event["top_element_info_points"] = event["top_element_info"][
                        "points"
                    ]
                except TypeError:
                    event["top_element_info_id"] = None
                    event["top_element_info_points"] = None
                event.pop("top_element_info")

        except IndexError:
            print("No current events")
            return

        with self.conn:
            self.conn.executemany(insert_query, events)

    def create_fixtures(self):
        """
        Inserts fixtures into the fixtures table
        """
        print("Fetching Fixtures table...")
        try:
            fixtures = fpl.get_fixtures()
        except IndexError:
            print("No fixtures")
            return

        insert_query = self.get_insert_query("fixtures")

        with self.conn:
            self.conn.executemany(insert_query, fixtures)

    def create_player_static(self):
        """
        Inserts players into the players_static table
        """
        print("Fetching player static info...")
        try:
            players = fpl.get_static_data("elements")
        except IndexError:
            print("No players")
            return

        insert_query = self.get_insert_query("players_static")

        with self.conn:
            self.conn.executemany(insert_query, players)

    def create_player_gw_detailed(self):
        """
        Updates player_gw_detailed table with player data for each gameweek
        """

        print("Fetching player detailed info...")
        self.cursor.execute("SELECT id FROM players_static")

        players = self.cursor.fetchall()
        players = [p[0] for p in players]

        insert_query = self.get_insert_query("player_gw_detailed")

        history = []
        with Pool(8) as p:
            with tqdm(total=len(players)) as pbar:
                for i, data in enumerate(
                    p.imap(partial(fpl.get_player_info, key="history"), players)
                ):
                    history.append(data)
                    pbar.update()

        with self.conn:
            for player in history:
                try:
                    self.conn.executemany(insert_query, player)
                except:
                    print("Error inserting player", player[0]["element"])
                    raise Exception

    def create_views(self):
        """
        Creates views for the database
        """

        with open("data_extraction/queries/create_views.sql", "r") as f:
            self.cursor.executescript(f.read())


def build_db_tables():
    try:
        os.remove("../data/FPL_DB.db")
    except FileNotFoundError:
        pass
    db = DBHandler()
    db.create_default_tables()
    db.static_inserts()
    db.create_events()
    db.create_fixtures()
    db.create_player_static()
    db.create_player_gw_detailed()
    db.create_views()
    db.conn.close()


if __name__ == "__main__":
    build_db_tables()
