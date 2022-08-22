from dash import Dash, dcc, html, dash_table as dt
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from src.data_extraction import db_handler as dbh

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

db = dbh.DBHandler()
query = """
SELECT t.short_name as team, f.event_number, f.fixture_difficulty, 
CASE WHEN is_home_team = 1 THEN opp.short_name||'(H)' ELSE opp.short_name||'(A)' END as opponent
FROM NEXT_FIVE_FIXTURES_BY_TEAM_VIEW f
JOIN TEAMS_STATIC opp
ON f.opponent_team = opp.id
JOIN TEAMS_STATIC t
on f.team_id = t.id
"""
df = pd.read_sql_query(query, db.conn)

fixtures_flat = pd.pivot(df, index="team", columns="event_number")
fixtures_flat.columns = fixtures_flat.columns.map(lambda x: f"{x[0]}_{x[1]}")

df = pd.read_sql_query("SELECT * FROM PLAYER_TABULAR_VIEW", db.conn).merge(
    fixtures_flat, how="inner", left_on="team_name", right_on="team"
)


def discrete_background_color_bins(df, n_bins=4, columns="all", columns_to_color="all"):
    import colorlover

    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    if columns == "all":
        if "id" in df:
            df_numeric_columns = df.select_dtypes("number").drop(["id"], axis=1)
        else:
            df_numeric_columns = df.select_dtypes("number")
        columns_to_color = df.select_dtypes("number").columns
    else:
        df_numeric_columns = df[columns]
    df_max = df_numeric_columns.max().max()
    df_min = df_numeric_columns.min().min()
    ranges = [((df_max - df_min) * i) + df_min for i in bounds]
    styles = []
    legend = []
    for i in range(1, len(bounds)):
        min_bound = ranges[i - 1]
        max_bound = ranges[i]
        color_scale = colorlover.scales[str(n_bins)]["div"]["RdYlGn"][::-1]
        backgroundColor = color_scale[i - 1]
        color = "white" if i > len(bounds) / 2.0 else "inherit"

        for column, col_column in zip(df_numeric_columns, columns_to_color):
            styles.append(
                {
                    "if": {
                        "filter_query": (
                            "{{{column}}} >= {min_bound}"
                            + (
                                " && {{{column}}} < {max_bound}"
                                if (i < len(bounds) - 1)
                                else ""
                            )
                        ).format(
                            column=column, min_bound=min_bound, max_bound=max_bound
                        ),
                        "column_id": col_column,
                    },
                    "backgroundColor": backgroundColor,
                    "color": color,
                }
            )
        legend.append(
            html.Div(
                style={"display": "inline-block", "width": "60px"},
                children=[
                    html.Div(
                        style={
                            "backgroundColor": backgroundColor,
                            "borderLeft": "1px rgb(50, 50, 50) solid",
                            "height": "10px",
                        }
                    ),
                    html.Small(round(min_bound, 2), style={"paddingLeft": "2px"}),
                ],
            )
        )

    return (styles, html.Div(legend, style={"padding": "5px 0 5px 0"}))


(styles, legend) = discrete_background_color_bins(
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
)

app.layout = dt.DataTable(
    df.to_dict("records"),
    page_size=20,
    style_table={"overflowX": "auto", "minWidth": "100%"},
    sort_action="native",
    sort_mode="multi",
    fixed_columns={"headers": True, "data": 3},
    style_cell={"minWidth": "150px", "width": "150px", "maxWidth": "150px"},
    style_data_conditional=styles,
)


if __name__ == "__main__":
    # dbh.build_db_tables()
    app.run_server(debug=True)
