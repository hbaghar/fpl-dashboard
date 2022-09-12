import dash
from dash import Dash, dcc, html, dash_table, Input, Output
import dash_bootstrap_components as dbc
from src.data_extraction import db_handler as dbh
import plotly.express as px
import pandas as pd

db = dbh.DBHandler()

df = pd.read_sql_query("SELECT * FROM PLAYER_WINDOW_METRICS_VIEW", db.conn)

dash.register_page(__name__, name="Player GW Statistics")

fig = px.line(x=df["round"], y=df["form"], color=df["web_name"])

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
                            options=db.get_table_columns("player_window_metrics_view"),
                            value="form",
                        ),
                        html.H5("Player Name"),
                        dcc.Dropdown(
                            id="player_dropdown",
                            options=db.get_unique_values_in_table_column(
                                "players_static", "web_name"
                            ),
                            multi=True,
                        ),
                    ],
                    width=2,
                    style={"border": "1px solid #f1f6ff", "padding": "5px"},
                ),
            ]
        ),
    ]
)


@dash.callback(
    Output("player_gw_graph", "figure"),
    Input("metric_dropdown", "value"),
    Input("player_dropdown", "value"),
)
def update_player_gw_graph(metric, player):
    if player is None:
        player = df["web_name"].unique()
    fig = px.line(
        df[df["web_name"].isin(player)],
        x="round",
        y=metric,
        color="web_name",
        title=f"{metric} over time",
    )
    return fig
