from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from data_extraction import db_handler as dbh

app = Dash(__name__)

db = dbh.DBHandler()
df = pd.read_sql_query("SELECT * FROM PLAYER_TABULAR_VIEW", db.conn)

fig = px.scatter(
    df,
    x="now_cost",
    y="total_points",
    color="team_name",
    size="goal_contribution",
    hover_data=["web_name", "team_name", "position", "total_points", "now_cost"],
)

app.layout = html.Div(
    children=[
        html.H1(children="Hello Dash"),
        html.Div(
            children="""
        Dash: A web application framework for your data.
    """
        ),
        dcc.Graph(id="example-graph", figure=fig),
    ]
)


if __name__ == "__main__":
    # dbh.build_db_tables()
    app.run_server(debug=True)
