import pandas as pd
from src.data_extraction import db_handler as dbh


def load_fixtures(db):
    query = """
    SELECT t.short_name as team, f.event_number, f.fixture_difficulty, 
    CASE WHEN is_home_team = 1 THEN opp.short_name||'(H)' ELSE opp.short_name||'(A)' END as opponent
    FROM NEXT_FIVE_FIXTURES_BY_TEAM_VIEW f
    JOIN TEAMS_STATIC opp
    ON f.opponent_team = opp.id
    JOIN TEAMS_STATIC t
    on f.team_id = t.id
    """
    fixtures = pd.read_sql_query(query, db.conn)

    fixtures_flat = pd.pivot(fixtures, index="team", columns="event_number")
    fixtures_flat.columns = fixtures_flat.columns.map(lambda x: f"{x[0]}_{x[1]}")

    return fixtures_flat


def load_players(db):
    return pd.read_sql_query("SELECT * FROM PLAYER_TABULAR_VIEW", db.conn)


def format_name_by_availability(df):
    df.loc[
        (df["chance_of_playing_this_round"] < 100)
        & (df["chance_of_playing_this_round"] >= 75),
        "web_name",
    ] = df["web_name"].apply(lambda x: f"🟡 {x}")

    df.loc[
        (df["chance_of_playing_this_round"] < 75)
        & (df["chance_of_playing_this_round"] >= 25),
        "web_name",
    ] = df["web_name"].apply(lambda x: f"🟠 {x}")

    df.loc[df["chance_of_playing_this_round"] == 0, "web_name"] = df["web_name"].apply(
        lambda x: f"🔴 {x}"
    )

    return df


def discrete_background_color_bins(
    df, n_bins=4, columns="all", columns_to_color="all", reverse=False
):
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
        color_scale = colorlover.scales[str(n_bins)]["div"]["RdYlGn"]
        if reverse:
            color_scale = color_scale[::-1]
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

    return styles
