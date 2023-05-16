import dash
from dash import Dash, dcc, html, dash_table as dt, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from yaml import safe_load
from src.data_extraction import db_handler as dbh
from src.utils import data_table_module as dtm
import os

pages_folder=os.path.join(os.path.dirname(__name__), "pages")
print(pages_folder)
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], use_pages=True, routes_pathname_prefix="/", name=__name__, pages_folder=pages_folder)
server = app.server

app.layout = html.Div(
    [
        dbc.Row(
            [html.H1("Fantasy Premier League")],
            style={
                "text-align": "center",
            },
        ),
        dbc.Row(
            [
                dbc.Navbar(
                    [
                        dbc.NavItem(
                            dbc.Button(
                                page["name"],
                                href=page["path"],
                                color="secondary",
                                style={"margin": "0 0 0 10px"},
                            )
                        )
                        for page in dash.page_registry.values()
                    ],
                    color="light",
                ),
            ]
        ),
        dash.page_container,
    ]
)


if __name__ == "__main__":
    # dbh.build_db_tables()
    app.run_server()
