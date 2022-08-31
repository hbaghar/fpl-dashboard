from dash import Dash, dcc, html, dash_table as dt
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from yaml import safe_load
from src.data_extraction import db_handler as dbh
from src.utils import data_table_module as dtm
from dash.dependencies import Input, Output

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
        dbc.Row(
            [html.H1("Fantasy Premier League: Player Tabular Statistics")],
            style={
                "text-align": "center",
            },
        ),
        dbc.Row(
            [
                dbc.Col(
                    dt.DataTable(
                        df.to_dict("records"),
                        id="player_table",
                        page_size=20,
                        style_table={
                            "overflowX": "auto",
                            "minWidth": "100%",
                        },
                        sort_action="native",
                        sort_mode="single",
                        sort_by=[{"column_id": "total_points", "direction": "desc"}],
                        fixed_columns={"headers": True, "data": 3},
                        style_cell={"minWidth": "150px", "maxWidth": "180px"},
                        style_data_conditional=styles_fixtures,
                        style_header={
                            "backgroundColor": "#f1f6ff",
                            "fontWeight": "bold",
                        },
                        columns=[
                            {
                                "name": config["column_names"][i],
                                "id": i,
                                "deletable": True,
                            }
                            for i in config["column_names"].keys()
                        ],
                        css=[{"selector": ".show-hide", "rule": "display: none"}],
                    ),
                    width=10,
                    style={"border": "1px solid #f1f6ff", "padding": "5px"},
                ),
                dbc.Col(
                    [
                        html.H5("Position"),
                        dcc.Dropdown(
                            id="position_dropdown",
                            options=config["position_options"],
                            value="All",
                            clearable=False,
                        ),
                    ],
                    width=2,
                    style={"border": "1px solid #f1f6ff", "padding": "5px"},
                ),
            ],
            style={"padding": "10px"},
        ),
    ]
)


@app.callback(
    Output("player_table", "data"),
    Output("player_table", "hidden_columns"),
    Input("position_dropdown", "value"),
)
def update_player_table(position):
    if position == "All":
        return df.to_dict("records"), config["all_players_hidden_columns"]
    else:
        hide_cols = (
            config["all_players_hidden_columns"]
            + config[position.lower() + "_hidden_columns"]
        )
        return df[df["position"] == position].to_dict("records"), hide_cols


if __name__ == "__main__":
    # dbh.build_db_tables()
    app.run_server(debug=True)
