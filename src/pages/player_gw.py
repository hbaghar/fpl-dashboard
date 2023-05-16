from re import I
import dash
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from src.data_extraction import db_handler as dbh
import plotly.express as px
from yaml import safe_load
import pandas as pd

db = dbh.DBHandler()

df = pd.read_sql_query("SELECT * FROM PLAYER_WINDOW_METRICS_VIEW", db.conn)

with open("utils/config.yml", "r") as yaml_file:
    config = safe_load(yaml_file)

dash.register_page(__name__, name="Player GW Statistics")

fig = px.line(
    df,
    x="round",
    y="form",
    color="id",
    markers=True,
    labels=config["gw_column_names"]
    | {"round": "Gameweek", "id": "Player", "team_name": "Team"},
    title=f"{config['gw_column_names']['form']} by Gameweek",
)
fig.for_each_trace(
    lambda t: t.update(name=df.loc[df.id.astype(str) == t.name, "web_name"].iloc[0])
)

layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [dcc.Graph(figure=fig, id="player_gw_graph")],
                    width=10,
                    style={"border": "1px solid #f1f6ff", "padding": "5px"},
                ),
                dbc.Col(
                    [
                        html.H5("Select Metric"),
                        dcc.Dropdown(
                            id="metric_dropdown",
                            options=[
                                {"label": value, "value": key}
                                for key, value in config["gw_column_names"].items()
                            ],
                            value="form",
                        ),
                        html.H5("Select Position"),
                        dcc.Dropdown(
                            id="position_dropdown",
                            options=db.get_unique_values_in_table_column(
                                "positions_static", "singular_name_short"
                            ),
                        ),
                        html.H5("Select Team"),
                        dcc.Dropdown(
                            id="team_dropdown",
                            options=db.get_unique_values_in_table_column(
                                "teams_static", "short_name"
                            ),
                            multi=True,
                        ),
                        html.H5("Player Name"),
                        dcc.Dropdown(
                            id="player_dropdown",
                            options=sorted(
                                db.get_unique_values_in_table_column(
                                    "players_static", "web_name"
                                )
                            ),
                            multi=True,
                        ),
                        html.I(
                            [
                                html.B("Note:"),
                                html.Br(),
                                "• When no player is selected, top 10 players are shown for the selected metric and current GW by default",
                                html.Br(),
                                "• Moving Averages are calculated over the last 5 GWs",
                                html.Br(),
                                "• Cumulative metrics are calculated over the entire season",
                            ]
                        ),
                    ],
                    width=2,
                    style={"border": "1px solid #f1f6ff", "padding": "5px"},
                ),
            ]
        ),
    ]
)


@dash.callback(Output("metric_dropdown", "value"), Input("metric_dropdown", "value"))
def update_metric_dropdown(metric):
    if metric is None:
        metric = "form"
    return metric


@dash.callback(
    Output("player_gw_graph", "figure"),
    Input("metric_dropdown", "value"),
    Input("team_dropdown", "value"),
    Input("position_dropdown", "value"),
    Input("player_dropdown", "value"),
)
def update_player_gw_graph(metric, team, position, player):
    if position is None or position == []:
        position = df["position"].unique()
    else:
        position = [position]
    if team is None or team == []:
        team = df["team_name"].unique()
    if player is None or player == []:
        df1 = df[(df["position"].isin(position)) & (df["team_name"].isin(team))]
        df1 = df1.sort_values(by=["round", metric], ascending=False)
        player = df1["id"].unique()[:10]
    else:
        player = df[df.web_name.isin(player)]["id"].unique()
    players = df[
        (df["id"].isin(player))
        & (df["position"].isin(position))
        & (df["team_name"].isin(team))
    ]
    fig = px.line(
        players,
        x="round",
        y=metric,
        color="id",
        markers=True,
        labels=config["gw_column_names"]
        | {"round": "Gameweek", "id": "Player ID", "team_name": "Team", "web_name": "Name", "position": "Position"},
        hover_data=["web_name", "team_name", "position"],
        title=f"{config['gw_column_names'][metric]} by Gameweek",
    )
    fig.for_each_trace(
        lambda t: t.update(name=df.loc[df.id.astype(str) == t.name, "web_name"].iloc[0])
    )
    return fig


@dash.callback(
    Output("player_dropdown", "options"),
    Input("position_dropdown", "value"),
    Input("team_dropdown", "value"),
)
def update_player_dropdown(position, team):
    if team is None or team == []:
        team = df["team_name"].unique()
    if position is None or position == []:
        position = df["position"].unique()
    else:
        position = [position]
    return sorted(
        df[(df["team_name"].isin(team)) & (df["position"].isin(position))][
            "web_name"
        ].unique()
    )
