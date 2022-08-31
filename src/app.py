from dash import Dash, dcc, html, dash_table as dt
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from yaml import safe_load
from src.data_extraction import db_handler as dbh
from src.utils import data_table_module as dtm

db = dbh.DBHandler()

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

with open("src/utils/config.yml", "r") as yaml_file:
    config = safe_load(yaml_file)

fixtures_flat = dtm.load_fixtures(db)
players = dtm.load_players(db)

df = players.merge(fixtures_flat, how="inner", left_on="team_name", right_on="team")
df = dtm.format_name_by_availability(df)


styles_fixtures = dtm.discrete_background_color_bins(
    df,
    columns_to_color=[
        "opponent_1",
        "opponent_2",
        "opponent_3",
        "opponent_4",
        "opponent_5",
    ],
    columns=[
        "fixture_difficulty_1",
        "fixture_difficulty_2",
        "fixture_difficulty_3",
        "fixture_difficulty_4",
        "fixture_difficulty_5",
    ],
    reverse=True,
)

app.layout = html.Div(
    [
        dt.DataTable(
            df.to_dict("records"),
            page_size=20,
            style_table={
                "overflowX": "auto",
                "minWidth": "100%",
                "padding": "15px",
            },
            sort_action="native",
            sort_mode="multi",
            fixed_columns={"headers": True, "data": 3},
            style_cell={"minWidth": "150px", "width": "150px", "maxWidth": "150px"},
            style_data_conditional=styles_fixtures,
            style_header={"backgroundColor": "#f1f6ff", "fontWeight": "bold"},
        ),
    ]
)


if __name__ == "__main__":
    # dbh.build_db_tables()
    app.run_server(debug=True)
