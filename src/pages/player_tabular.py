import dash
from dash import Dash, dcc, html, dash_table as dt, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
from yaml import safe_load

from src.data_extraction import db_handler as dbh
from src.utils import data_table_module as dtm

db = dbh.DBHandler()

dash.register_page(__name__, name="Player Overall Statistics")

with open("utils/config.yml", "r") as yaml_file:
    config = safe_load(yaml_file)

fixtures_flat = dtm.load_fixtures(db)
players = dtm.load_players(db)

df = players.merge(fixtures_flat, how="inner", left_on="team_name", right_on="team")
df = dtm.format_name_by_availability(df)


# styles_fixtures = dtm.discrete_background_color_bins(
#     df,
#     columns_to_color=[
#         "opponent_1",
#         "opponent_2",
#         "opponent_3",
#         "opponent_4",
#         "opponent_5",
#     ],
#     columns=[
#         "fixture_difficulty_1",
#         "fixture_difficulty_2",
#         "fixture_difficulty_3",
#         "fixture_difficulty_4",
#         "fixture_difficulty_5",
#     ],
#     reverse=True,
# )

layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.H5("X-axis"),
                                    dcc.Dropdown(
                                        id="x_axis",
                                        options=[
                                            {
                                                "label": config["static_column_names"][
                                                    i
                                                ],
                                                "value": i,
                                            }
                                            for i in config[
                                                "static_column_names"
                                            ].keys()
                                            if i
                                            not in [
                                                "web_name",
                                                "team_name",
                                                "position",
                                                "opponent_1",
                                                "opponent_2",
                                                "opponent_3",
                                                "opponent_4",
                                                "opponent_5",
                                            ]
                                        ],
                                        value="expected_goal_involvements",
                                        clearable=False,
                                    ),
                                ]
                            ),
                            dbc.Col(
                                [
                                    html.H5("Y-axis"),
                                    dcc.Dropdown(
                                        id="y_axis",
                                        options=[
                                            {
                                                "label": config["static_column_names"][
                                                    i
                                                ],
                                                "value": i,
                                            }
                                            for i in config[
                                                "static_column_names"
                                            ].keys()
                                            if i
                                            not in [
                                                "web_name",
                                                "team_name",
                                                "position",
                                                "opponent_1",
                                                "opponent_2",
                                                "opponent_3",
                                                "opponent_4",
                                                "opponent_5",
                                            ]
                                        ],
                                        value="goal_involvements",
                                        clearable=False,
                                    ),
                                ]
                            ),
                            dbc.Col(
                                [
                                    html.H5("Size"),
                                    dcc.Dropdown(
                                        id="bubble_size",
                                        options=[
                                            {
                                                "label": config["static_column_names"][
                                                    i
                                                ],
                                                "value": i,
                                            }
                                            for i in config[
                                                "static_column_names"
                                            ].keys()
                                            if i
                                            not in ["web_name", "team_name", "position"]
                                        ],
                                        value="form",
                                    ),
                                ]
                            ),
                            dcc.Graph(id="scatter"),
                            dt.DataTable(
                                df.to_dict("records"),
                                id="player_table",
                                page_size=15,
                                style_table={
                                    "overflowX": "auto",
                                    "minWidth": "100%",
                                },
                                sort_action="native",
                                sort_mode="single",
                                fixed_columns={"headers": True, "data": 3},
                                style_cell={"minWidth": "150px", "maxWidth": "180px"},
                                # style_data_conditional=styles_fixtures,
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
                                css=[
                                    {"selector": ".show-hide", "rule": "display: none"}
                                ],
                            ),
                        ]
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
                            marks=None,
                            tooltip={
                                "always_visible": True,
                                "placement": "bottom",
                            },
                        ),
                        html.H5("Price Range"),
                        dcc.RangeSlider(
                            id="price_range_slider",
                            min=df.now_cost.min(),
                            max=df.now_cost.max(),
                            value=[df.now_cost.min(), df.now_cost.max()],
                            step=0.1,
                            marks=None,
                            tooltip={
                                "always_visible": True,
                                "placement": "bottom",
                            },
                        ),
                        dbc.Button(
                            "Reset Filters",
                            id="reset_button",
                            color="danger",
                            style={"margin-top": "5px"},
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
    Output("scatter", "figure"),
    Input("x_axis", "value"),
    Input("y_axis", "value"),
    Input("bubble_size", "value"),
    Input("position_dropdown", "value"),
    Input("team_dropdown", "value"),
    Input("minutes_played_slider", "value"),
    Input("price_range_slider", "value"),
)
def update_scatter(
    x_axis,
    y_axis,
    bubble_size,
    position_dropdown_value,
    team_dropdown_value,
    minutes_played_slider_value,
    price_range_slider_value,
):
    dff = filter_df(
        position_dropdown_value,
        team_dropdown_value,
        minutes_played_slider_value,
        price_range_slider_value,
    )
    if bubble_size:
        dff = dff[dff[bubble_size] >= 0]
    dff["id"] = dff["id"].astype(str)
    fig = px.scatter(
        dff,
        x=x_axis,
        y=y_axis,
        color="id",
        size=bubble_size,
        labels=config["static_column_names"] | {"id": "Player ID", "web_name": "Name", "team_name": "Team", "position": "Position"},
        hover_data=['web_name', 'team_name', 'position']
    )
    fig.update_layout(
        title=f"{config['static_column_names'][y_axis]} by {config['static_column_names'][x_axis]}",
        xaxis_title=config["static_column_names"][x_axis],
        yaxis_title=config["static_column_names"][y_axis],
    )
    fig.for_each_trace(
        lambda t: t.update(
            name=dff.loc[dff.id.astype(str) == t.name, "web_name"].iloc[0]
        )
    )
    fig.for_each_trace(
        lambda t: t.update(showlegend=False if t.marker.size == [0] else True)
    )

    return fig


@dash.callback(
    Output("player_table", "data"),
    Output("player_table", "hidden_columns"),
    Output("player_table", "sort_by"),
    Input("position_dropdown", "value"),
    Input("team_dropdown", "value"),
    Input("minutes_played_slider", "value"),
    Input("price_range_slider", "value"),
    Input("scatter", "relayoutData"),
    Input("x_axis", "value"),
    Input("y_axis", "value"),
)
def update_player_table(
    position_dropdown_value,
    team_dropdown_value,
    minutes_played_slider_value,
    price_range_slider_value,
    relayoutData,
    x_axis,
    y_axis,
):

    dff = filter_df(
        position_dropdown_value,
        team_dropdown_value,
        minutes_played_slider_value,
        price_range_slider_value,
    )
    if relayoutData and "xaxis.range[0]" in relayoutData:
        # Filtering dataframe based on current zoom
        dff = dff[
            (dff[x_axis] >= relayoutData["xaxis.range[0]"])
            & (dff[x_axis] <= relayoutData["xaxis.range[1]"])
        ]
    if relayoutData and "yaxis.range[0]" in relayoutData:
        dff = dff[
            (dff[y_axis] >= relayoutData["yaxis.range[0]"])
            & (dff[y_axis] <= relayoutData["yaxis.range[1]"])
        ]
    hide_cols = config["all_players_hidden_columns"]
    if position_dropdown_value != None:
        hide_cols = (
            hide_cols + config[str.lower(position_dropdown_value) + "_hidden_columns"]
        )

    return (
        dff.to_dict("records"),
        hide_cols,
        [{"column_id": y_axis, "direction": "desc"}],
    )


def filter_df(
    position_dropdown_value,
    team_dropdown_value,
    minutes_played_slider_value,
    price_range_slider_value,
):
    dff = df.copy()
    if position_dropdown_value != None:
        dff = dff[dff.position == position_dropdown_value]
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
    return dff


@dash.callback(
    Output("position_dropdown", "value"),
    Output("team_dropdown", "value"),
    Output("minutes_played_slider", "value"),
    Output("price_range_slider", "value"),
    Output("scatter", "relayoutData"),
    Input("reset_button", "n_clicks"),
)
def reset_filters(n_clicks):
    return (
        None,
        [],
        [0, df.minutes.max()],
        [df.now_cost.min(), df.now_cost.max()],
        {
            "xaxis.autorange": True,
            "xaxis.showspikes": False,
            "yaxis.autorange": True,
            "yaxis.showspikes": False,
        },
    )
