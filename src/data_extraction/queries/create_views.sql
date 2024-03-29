CREATE VIEW IF NOT EXISTS PLAYER_TABULAR_VIEW AS
SELECT
    player.id,
    player.web_name,
    position.singular_name_short AS position,
    team.short_name AS team_name,
    player.total_points,
    player.now_cost * 1.0 / 10 AS now_cost,
    player.selected_by_percent,
    player.event_points,
    player.goals_scored,
    player.assists,
    player.goals_scored + player.assists AS goal_involvements,
    CASE
        WHEN player.goals_scored = 0 THEN 0
        ELSE ROUND(
            player.goals_scored * 1.0 / player.minutes * 90,
            3
        )
    END AS goals_per_90,
    CASE
        WHEN player.assists = 0 THEN 0
        ELSE ROUND(player.assists * 1.0 / player.minutes * 90, 3)
    END AS assists_per_90,
    CASE
        WHEN player.goals_scored + player.assists = 0 THEN 0
        ELSE ROUND(
            (player.goals_scored + player.assists) * 1.0 / player.minutes * 90,
            3
        )
    END AS goal_involvements_per_90,
    player.form,
    player.clean_sheets,
    player.goals_conceded,
    CASE
        WHEN player.goals_conceded = 0 THEN 0
        ELSE ROUND(
            player.goals_conceded * 1.0 / player.minutes * 90,
            3
        )
    END AS goals_conceded_per_90,
    -- include xg stats from players_static
    player.expected_assists,
    player.expected_goals,
    player.expected_goal_involvements,
    player.expected_goals_conceded,
    player.expected_assists_per_90,
    player.expected_goals_per_90,
    player.expected_goal_involvements_per_90,
    player.expected_goals_conceded_per_90,
    player.own_goals,
    player.penalties_saved,
    player.penalties_missed,
    player.yellow_cards,
    player.red_cards,
    player.saves,
    player.minutes,
    player.bonus,
    player.bps,
    player.influence,
    player.creativity,
    player.threat,
    player.ict_index,
    player.value_form,
    player.value_season,
    player.points_per_game,
    CASE
        WHEN player.chance_of_playing_this_round IS NOT NULL THEN player.chance_of_playing_this_round
        ELSE 100
    END AS chance_of_playing_this_round
FROM
    players_static player
    INNER JOIN teams_static team ON player.team = team.id
    INNER JOIN positions_static position ON player.element_type = position.id;

CREATE VIEW IF NOT EXISTS CURRENT_GW_VIEW AS
SELECT
    id
FROM
    events_static
WHERE
    is_current = 1;

CREATE VIEW IF NOT EXISTS NEXT_FIVE_FIXTURES_RAW AS
SELECT
    fixture.id,
    fixture.event,
    fixture.team_h AS home_team,
    fixture.team_a AS away_team,
    fixture.team_h_difficulty AS home_team_difficulty,
    fixture.team_a_difficulty AS away_team_difficulty
FROM
    fixtures fixture
WHERE
    fixture.event BETWEEN (
        SELECT
            id
        FROM
            CURRENT_GW_VIEW
    ) + 1
    AND (
        SELECT
            id
        FROM
            CURRENT_GW_VIEW
    ) + 5
ORDER BY
    event;

CREATE VIEW IF NOT EXISTS NEXT_FIVE_FIXTURES_BY_TEAM_VIEW AS
SELECT
    team.id as team_id,
    v.event,
    ROW_NUMBER() OVER (
        PARTITION BY team.id
        ORDER BY
            v.event
    ) AS event_number,
    CASE
        WHEN v.home_team = team.id THEN 1
        ELSE 0
    END AS is_home_team,
    CASE
        WHEN team.id = v.home_team THEN v.home_team_difficulty
        ELSE v.away_team_difficulty
    END AS fixture_difficulty,
    CASE
        WHEN team.id = v.home_team THEN v.away_team
        ELSE v.home_team
    END AS opponent_team
FROM
    teams_static team
    INNER JOIN NEXT_FIVE_FIXTURES_RAW v ON v.home_team = team.id
    OR v.away_team = team.id
ORDER BY
    team.id,
    v.event;

CREATE VIEW IF NOT EXISTS PLAYER_WINDOW_METRICS_VIEW AS
SELECT
    player.id,
    player.web_name,
    player.position,
    player.team_name,
    a.*,
    ROUND(
        a.cumulative_goals_scored * 1.0 / a.cumulative_minutes * 90,
        2
    ) AS cumulative_goals_per_90,
    ROUND(
        a.cumulative_assists * 1.0 / a.cumulative_minutes * 90,
        2
    ) AS cumulative_assists_per_90,
    ROUND(
        a.cumulative_goal_involvements * 1.0 / a.cumulative_minutes * 90,
        2
    ) AS cumulative_goal_involvements_per_90
FROM
    (
        SELECT
            *,
            SUM(total_points) OVER (
                PARTITION BY element
                ORDER BY
                    round ROWS BETWEEN UNBOUNDED PRECEDING
                    AND CURRENT ROW
            ) AS cumulative_points,
            ROUND(
                AVG(bonus) OVER (
                    PARTITION BY element
                    ORDER BY
                        round ROWS BETWEEN 4 PRECEDING
                        AND CURRENT ROW
                ),
                1
            ) AS average_bonus,
            ROUND(
                AVG(bps) OVER (
                    PARTITION BY element
                    ORDER BY
                        round ROWS BETWEEN 4 PRECEDING
                        AND CURRENT ROW
                ),
                1
            ) AS average_bps,
            SUM(assists) OVER (
                PARTITION BY element
                ORDER BY
                    round ROWS BETWEEN UNBOUNDED PRECEDING
                    AND CURRENT ROW
            ) AS cumulative_assists,
            SUM(clean_sheets) OVER (
                PARTITION BY element
                ORDER BY
                    round ROWS BETWEEN UNBOUNDED PRECEDING
                    AND CURRENT ROW
            ) AS cumulative_clean_sheets,
            SUM(goals_scored) OVER (
                PARTITION BY element
                ORDER BY
                    round ROWS BETWEEN UNBOUNDED PRECEDING
                    AND CURRENT ROW
            ) AS cumulative_goals_scored,
            SUM(goals_conceded) OVER (
                PARTITION BY element
                ORDER BY
                    round ROWS BETWEEN UNBOUNDED PRECEDING
                    AND CURRENT ROW
            ) AS cumulative_goals_conceded,
            SUM(saves) OVER (
                PARTITION BY element
                ORDER BY
                    round ROWS BETWEEN UNBOUNDED PRECEDING
                    AND CURRENT ROW
            ) AS cumulative_saves,
            ROUND(
                AVG(influence) OVER (
                    PARTITION BY element
                    ORDER BY
                        round ROWS BETWEEN 4 PRECEDING
                        AND CURRENT ROW
                ),
                1
            ) AS average_influence,
            ROUND(
                AVG(creativity) OVER (
                    PARTITION BY element
                    ORDER BY
                        round ROWS BETWEEN 4 PRECEDING
                        AND CURRENT ROW
                ),
                1
            ) AS average_creativity,
            ROUND(
                AVG(threat) OVER (
                    PARTITION BY element
                    ORDER BY
                        round ROWS BETWEEN 4 PRECEDING
                        AND CURRENT ROW
                ),
                1
            ) AS average_threat,
            ROUND(
                AVG(ict_index) OVER (
                    PARTITION BY element
                    ORDER BY
                        round ROWS BETWEEN 4 PRECEDING
                        AND CURRENT ROW
                ),
                1
            ) AS average_ict_index,
            ROUND(
                AVG(expected_assists) OVER (
                    PARTITION BY element
                    ORDER BY
                        round ROWS BETWEEN 4 PRECEDING
                        AND CURRENT ROW
                ),
                2
            ) AS average_xa,
            ROUND(
                AVG(expected_goals_conceded) OVER (
                    PARTITION BY element
                    ORDER BY
                        round ROWS BETWEEN 4 PRECEDING
                        AND CURRENT ROW
                ),
                2
            ) AS average_xgc,
            ROUND(
                AVG(expected_goals) OVER (
                    PARTITION BY element
                    ORDER BY
                        round ROWS BETWEEN 4 PRECEDING
                        AND CURRENT ROW
                ),
                2
            ) AS average_xg,
            ROUND(
                AVG(expected_goal_involvements) OVER (
                    PARTITION BY element
                    ORDER BY
                        round ROWS BETWEEN 4 PRECEDING
                        AND CURRENT ROW
                ),
                2
            ) AS average_xgi,
            ROUND(
                AVG(total_points) OVER (
                    PARTITION BY element
                    ORDER BY
                        round ROWS BETWEEN 4 PRECEDING
                        AND CURRENT ROW
                ),
                1
            ) AS form,
            SUM(goals_scored + assists) OVER (
                PARTITION BY element
                ORDER BY
                    round ROWS BETWEEN UNBOUNDED PRECEDING
                    AND CURRENT ROW
            ) AS cumulative_goal_involvements,
            SUM(minutes) OVER (
                PARTITION BY element
                ORDER BY
                    round ROWS BETWEEN UNBOUNDED PRECEDING
                    AND CURRENT ROW
            ) AS cumulative_minutes,
             ROUND(SUM(expected_assists) OVER (
                PARTITION BY element
                ORDER BY
                    round ROWS BETWEEN UNBOUNDED PRECEDING
                    AND CURRENT ROW
                ),
                2
            ) AS cumulative_xa,
            ROUND(SUM(expected_goals) OVER (
                PARTITION BY element
                ORDER BY
                    round ROWS BETWEEN UNBOUNDED PRECEDING
                    AND CURRENT ROW
                ),
                2
            ) AS cumulative_xg,
            ROUND(SUM(expected_goal_involvements) OVER (
                PARTITION BY element
                ORDER BY
                    round ROWS BETWEEN UNBOUNDED PRECEDING
                    AND CURRENT ROW
                ),
                2
            ) AS cumulative_xgi,
            ROUND(SUM(expected_goals_conceded) OVER (
                PARTITION BY element
                ORDER BY
                    round ROWS BETWEEN UNBOUNDED PRECEDING
                    AND CURRENT ROW
                ),
                2
            ) AS cumulative_xgc
        FROM
            player_gw_detailed
    ) a
    INNER JOIN PLAYER_TABULAR_VIEW player ON a.element = player.id;