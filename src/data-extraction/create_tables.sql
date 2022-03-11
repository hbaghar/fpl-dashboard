CREATE TABLE IF NOT EXISTS teams_static (id INTEGER PRIMARY KEY, name TEXT, code INTEGER, short_name TEXT);

CREATE TABLE IF NOT EXISTS positions_static (id INTEGER PRIMARY KEY, singular_name_short TEXT, squad_max_play INTEGER, squad_min_play INTEGER);

CREATE TABLE IF NOT EXISTS players_static (id INTEGER PRIMARY KEY, first_name TEXT, second_name TEXT, web_name TEXT, team INTEGER, element_type INTEGER, 
                                                assists INTEGER, bonus INTEGER, bps INTEGER, chance_of_playing_next_round INTEGER, chance_of_playing_this_round INTEGER,
                                                clean_sheets INTEGER, code INTEGER, corners_and_indirect_freekicks_order INTEGER, corners_and_indirect_freekicks_text TEXT,
                                                cost_change_event INTEGER, cost_change_start INTEGER, creativity DOUBLE, creativity_rank INTEGER, creativity_rank_type INTEGER,
                                                direct_freekicks_order INTEGER, direct_freekicks_text TEXT, dreamteam_count INTEGER,
                                                ep_next DOUBLE, event_points INTEGER, form DOUBLE , goals_conceded INTEGER, goals_scored INTEGER,
                                                ict_index DOUBLE, ict_index_rank INTEGER, ict_index_rank_type INTEGER,
                                                influence DOUBLE, influence_rank INTEGER, influence_rank_type INTEGER, minutes INTEGER,
                                                news TEXT, news_added TEXT, now_cost INTEGER, own_goals INTEGER,
                                                penalties_missed INTEGER, penalties_order INTEGER, penalties_saved INTEGER, penalties_text TEXT, photo TEXT,
                                                points_per_game INTEGER, red_cards INTEGER, saves INTEGER, selected_by_percent DOUBLE, 
                                                threat DOUBLE, threat_rank INTEGER, threat_rank_type INTEGER, total_points INTEGER,
                                                value_form DOUBLE, value_season DOUBLE, yellow_cards INTEGER,
                                                FOREIGN KEY(team) REFERENCES teams(id), FOREIGN KEY(element_type) REFERENCES positions(id));
        
CREATE TABLE IF NOT EXISTS metric_names_static (name TEXT PRIMARY KEY, label TEXT);
        
CREATE TABLE IF NOT EXISTS events_static (id INTEGER PRIMARY KEY, average_entry_score INTEGER, data_checked TEXT, deadline_time TEXT, finished TEXT, highest_score INTEGER, 
                                                    is_current TEXT, is_next TEXT, is_previous TEXT, most_captained INTEGER, most_selected INTEGER, 
                                                    most_transferred_in INTEGER, most_vice_captained INTEGER,
                                                    name TEXT, top_element INTEGER, top_element_info_id INTEGER, top_element_info_points INTEGER, transfers_made INTEGER);
        
CREATE TABLE IF NOT EXISTS fixtures (id INTEGER PRIMARY KEY, event INTEGER, team_a INTEGER, team_h INTEGER, team_a_difficulty INTEGER, team_h_difficulty INTEGER);
        
CREATE TABLE IF NOT EXISTS player_gw_detailed (element INTEGER, assists INTEGER, bonus INTEGER, bps INTEGER, clean_sheets INTEGER, creativity DOUBLE, fixture INTEGER, 
                                                        goals_conceded INTEGER, goals_scored INTEGER, ict_index DOUBLE, influence DOUBLE, kickoff_time TEXT, 
                                                        minutes INTEGER, opponent_team INTEGER, own_goals INTEGER, penalties_missed INTEGER, penalties_saved INTEGER, 
                                                        red_cards INTEGER, round INTEGER, saves INTEGER, selected INTEGER, team_a_score INTEGER, 
                                                        team_h_score INTEGER, threat DOUBLE, total_points INTEGER, transfers_balance INTEGER, transfers_in INTEGER, 
                                                        transfers_out INTEGER, value INTEGER, was_home TEXT, yellow_cards INTEGER,
                                                        CONSTRAINT player_week_fixture PRIMARY KEY (element, round, fixture), FOREIGN KEY(element) REFERENCES players(id), FOREIGN KEY(fixture) REFERENCES fixtures(id));