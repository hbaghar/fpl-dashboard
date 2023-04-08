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
        dbc.Row(
            [
                dbc.Col(
                    [html.H5("View top performers by", style={"text-align": "center"})],
                    width=2,
                    style={"margin": "5px -40px 0 5px"},
                ),
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id="top-performers-dropdown",
                            options=["Gameweek", "Season"],
                            value="Gameweek",
                            clearable=False,
                        ),
                    ],
                    width=2,
                ),
                dcc.Graph(id="top-performers-graph"),
            ]
        ),
    ],
)


@dash.callback(Output("current-gw", "children"), Input("current-gw", "n_clicks"))
def update_current_gw(placeholder):
    db = dbh.DBHandler()
    current_gw = pd.read_sql_query("SELECT * FROM current_gw_view", db.conn).iloc[0, 0]
    db.conn.close()

    return f"Current Gameweek:{current_gw}"


@dash.callback(
    Output("top-performers-graph", "figure"), Input("top-performers-dropdown", "value")
)
def top_players_graph(value):
    db = dbh.DBHandler()
    if value == "Gameweek":
        score_var = "event_points"
    elif value == "Season":
        score_var = "total_points"

    current_gw = pd.read_sql_query("SELECT * FROM current_gw_view", db.conn).iloc[0, 0]
    df = pd.read_sql_query(
        f"""
            SELECT id, web_name, position, team_name, {score_var}
            FROM  (
                SELECT 
                    id, web_name, position, team_name, {score_var},
                    rank() OVER (PARTITION BY position ORDER BY {score_var} DESC) AS rank
                FROM 
                    player_tabular_view
                )
            WHERE 
                rank <= 5
            ORDER BY
                rank
        """,
        db.conn,
    )
    db.conn.close()
    fig = px.bar(
        data_frame=df.sort_values(by=score_var, ascending=True),
        y="web_name",
        x=score_var,
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
        title=f"Top performers this {value.lower()}",
        height=500,
        category_orders={"position": ["GKP", "DEF", "MID", "FWD"]},
    )
    fig.update_layout(barmode="stack", yaxis={"categoryorder": "total ascending"})
    fig.for_each_annotation(lambda t: t.update(text=t.text.split("=")[-1]))
    fig.update_yaxes(matches=None, showticklabels=True, title=None)
    return fig
