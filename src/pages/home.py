import dash
from dash import Dash, dcc, html, dash_table, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
from yaml import safe_load
from src.data_extraction import db_handler as dbh
import plotly.express as px

dash.register_page(__name__, name="Home", path="/")

layout = html.Div(
    [
        html.H2(id="current-gw", style={"text-align": "center"}),
        dcc.Graph(id="top5-players"),
    ],
)


@dash.callback(Output("current-gw", "children"), Input("current-gw", "n_clicks"))
def update_current_gw(placeholder):
    db = dbh.DBHandler()
    current_gw = pd.read_sql_query("SELECT * FROM current_gw_view", db.conn).iloc[0, 0]
    db.conn.close()

    return f"Current Gameweek:{current_gw}"


@dash.callback(Output("top5-players", "figure"), Input("current-gw", "n_clicks"))
def top5_players(placeholder):
    db = dbh.DBHandler()
    current_gw = pd.read_sql_query("SELECT * FROM current_gw_view", db.conn).iloc[0, 0]
    df = pd.read_sql_query(
        f"""
                            SELECT id, web_name, position, team_name, total_points
                            FROM  (
                                SELECT 
                                    id, web_name, total_points, team_name, position,
                                    rank() OVER (PARTITION BY position ORDER BY total_points DESC) AS rank
                                FROM 
                                    player_window_metrics_view
                                WHERE 
                                    round = {current_gw})
                            WHERE 
                                rank <= 5
                            ORDER BY
                                rank
                           """,
        db.conn,
    )
    db.conn.close()
    fig = px.bar(
        data_frame=df.sort_values(by=["total_points"], ascending=True),
        y="web_name",
        x="total_points",
        facet_col="position",
        facet_col_wrap=2,
        facet_col_spacing=0.1,
        facet_row_spacing=0.1,
        color="team_name",
        orientation="h",
        labels={
            "web_name": "Player",
            "total_points": "Round Points",
            "team_name": "Team",
        },
        title="Top performers this gameweek",
        height=500,
        category_orders={"position": ["GKP", "DEF", "MID", "FWD"]},
    )
    fig.update_layout(barmode="stack", yaxis={"categoryorder": "total ascending"})
    fig.for_each_annotation(lambda t: t.update(text=t.text.split("=")[-1]))
    fig.update_yaxes(matches=None, showticklabels=True, title=None)
    return fig
