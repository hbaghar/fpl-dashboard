import dash
from dash import Dash, dcc, html, dash_table, Input, Output
import pandas as pd
from yaml import safe_load
from src.data_extraction import db_handler as dbh

db = dbh.DBHandler()

dash.register_page(__name__, name="Home", path="/")

current_gw = pd.read_sql_query("SELECT * FROM current_gw_view", db.conn).iloc[0, 0]

layout = html.Div(
    [
        html.H2(f"Current Gameweek:{current_gw}", style={"text-align": "center"}),
    ]
)
