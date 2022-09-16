import dash
from dash import Dash, dcc, html, dash_table as dt, Input, Output
import dash_bootstrap_components as dbc
from yaml import safe_load

from src.data_extraction import db_handler as dbh
from src.utils import data_table_module as dtm

db = dbh.DBHandler()

dash.register_page(__name__, name="Player Overall Statistics")

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

layout = html.Div(
    [
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
                                "name": config["static_column_names"][i],
                                "id": i,
                            }
                            for i in config["static_column_names"].keys()
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
                            options=db.get_unique_values_in_table_column(
                                "positions_static", "singular_name_short"
                            ),
                            placeholder="All",
                        ),
                        html.H5("Team"),
                        dcc.Dropdown(
                            id="team_dropdown",
                            options=db.get_unique_values_in_table_column(
                                "teams_static", "short_name"
                            ),
                            placeholder="All",
                            multi=True,
                        ),
                        html.H5("Minutes Played"),
                        dcc.RangeSlider(
                            id="minutes_played_slider",
                            min=0,
                            max=df.minutes.max(),
                            value=[0, df.minutes.max()],
                        ),
                        html.H5("Price Range"),
                        dcc.RangeSlider(
                            id="price_range_slider",
                            min=df.now_cost.min(),
                            max=df.now_cost.max(),
                            value=[df.now_cost.min(), df.now_cost.max()],
                        ),
                        dbc.Button(
                            "Reset Filters",
                            id="reset_button",
                            color="danger",
                        ),
                    ],
                    width=2,
                    style={
                        "border": "1px solid #f1f6ff",
                        "padding": "5px",
                    },
                ),
            ],
            style={"padding": "10px"},
        ),
    ]
)


@dash.callback(
    Output("player_table", "data"),
    Output("player_table", "hidden_columns"),
    Input("position_dropdown", "value"),
    Input("team_dropdown", "value"),
    Input("minutes_played_slider", "value"),
    Input("price_range_slider", "value"),
)
def update_player_table(
    position_dropdown_value,
    team_dropdown_value,
    minutes_played_slider_value,
    price_range_slider_value,
):
    hide_cols = config["all_players_hidden_columns"]
    dff = df.copy()
    if position_dropdown_value != None:
        dff = dff[dff.position == position_dropdown_value]
        hide_cols += config[position_dropdown_value.lower() + "_hidden_columns"]
    if team_dropdown_value != [] and team_dropdown_value != None:
        dff = dff[dff.team_name.isin(team_dropdown_value)]
    dff = dff[
        (dff.minutes >= minutes_played_slider_value[0])
        & (dff.minutes <= minutes_played_slider_value[1])
    ]
    dff = dff[
        (dff.now_cost >= price_range_slider_value[0])
        & (dff.now_cost <= price_range_slider_value[1])
    ]
    return dff.to_dict("records"), hide_cols


@dash.callback(
    Output("position_dropdown", "value"),
    Output("team_dropdown", "value"),
    Output("minutes_played_slider", "value"),
    Output("price_range_slider", "value"),
    Input("reset_button", "n_clicks"),
)
def reset_filters(n_clicks):
    return None, [], [0, df.minutes.max()], [df.now_cost.min(), df.now_cost.max()]
