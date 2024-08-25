from enum import Enum
from typing import List, NamedTuple, Optional

import numpy as np
from pydantic import computed_field
from sqlmodel import (JSON, Column, Field, PrimaryKeyConstraint, Relationship,
                      SQLModel, create_engine)


class Event(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    deadline_time: str
    average_entry_score: int
    finished: bool
    data_checked: bool
    highest_scoring_entry: Optional[int]
    deadline_time_epoch: int
    deadline_time_game_offset: int
    highest_score: Optional[int]
    is_previous: bool
    is_current: bool
    is_next: bool
    # chip_plays: List[dict] = Field(default=[], sa_type=Column(JSON))
    most_selected: Optional[int]
    most_transferred_in: Optional[int]
    top_element: Optional[int]
    # top_element_info: Optional[dict] = Field(default_factory={}, sa_type=Column(JSON))
    transfers_made: int
    most_captained: Optional[int]
    most_vice_captained: Optional[int]


class Team(SQLModel, table=True):
    code: int
    draw: int
    form: Optional[float]
    id: int = Field(primary_key=True)
    loss: int
    name: str
    played: int
    points: int
    position: int
    short_name: str
    strength: int
    team_division: Optional[str]
    unavailable: bool
    win: int
    strength_overall_home: int
    strength_overall_away: int
    strength_attack_home: int
    strength_attack_away: int
    strength_defence_home: int
    strength_defence_away: int
    pulse_id: int

    team_players: List["Element"] = Relationship(back_populates="player_team")


from collections import namedtuple
from typing import List, NamedTuple


class PlayerStats(NamedTuple):
    points: float
    goal_involvements: float
    xgi: float
    goals_conceded: float
    xgc: float


def calculate_home_away_stats(
    games: List["PlayerHistory"], is_home: bool, per_90: bool = False
) -> PlayerStats:
    filtered_games = [g for g in games if g.was_home == is_home and g.minutes > 0]
    minutes = sum(g.minutes for g in filtered_games)
    if minutes == 0:
        return PlayerStats(0.0, 0.0, 0.0, 0.0, 0.0)

    points = sum(g.total_points for g in filtered_games)
    goal_involvements = sum(g.goals_scored + g.assists for g in filtered_games)
    xgi = sum(g.expected_goal_involvements for g in filtered_games)
    goals_conceded = sum(g.goals_conceded for g in filtered_games)
    xgc = sum(g.expected_goals_conceded for g in filtered_games)

    if per_90:
        points = points / minutes * 90
        goal_involvements = goal_involvements / minutes * 90
        xgi = xgi / minutes * 90
        goals_conceded = goals_conceded / minutes * 90
        xgc = xgc / minutes * 90

    return PlayerStats(points, goal_involvements, xgi, goals_conceded, xgc)


class Element(SQLModel, table=True):
    chance_of_playing_next_round: Optional[int]
    chance_of_playing_this_round: Optional[int]
    code: int
    cost_change_event: int
    cost_change_event_fall: int
    cost_change_start: int
    cost_change_start_fall: int
    dreamteam_count: int
    element_type: int = Field(foreign_key="elementtype.id")
    ep_next: str
    ep_this: str
    event_points: int
    first_name: str
    form: float
    id: int = Field(primary_key=True)
    in_dreamteam: bool
    news: str
    news_added: Optional[str]
    now_cost: int
    photo: str
    points_per_game: float
    second_name: str
    selected_by_percent: float
    special: bool
    squad_number: Optional[int]
    status: str
    team: int = Field(foreign_key="team.id")
    team_code: int
    total_points: int
    transfers_in: int
    transfers_in_event: int
    transfers_out: int
    transfers_out_event: int
    value_form: float
    value_season: float
    web_name: str
    minutes: int
    goals_scored: int
    assists: int
    clean_sheets: int
    goals_conceded: int
    own_goals: int
    penalties_saved: int
    penalties_missed: int
    yellow_cards: int
    red_cards: int
    saves: int
    bonus: int
    bps: int
    influence: float
    creativity: float
    threat: float
    ict_index: float
    starts: int
    expected_goals: float
    expected_assists: float
    expected_goal_involvements: float
    expected_goals_conceded: float
    influence_rank: int
    influence_rank_type: int
    creativity_rank: int
    creativity_rank_type: int
    threat_rank: int
    threat_rank_type: int
    ict_index_rank: int
    ict_index_rank_type: int
    corners_and_indirect_freekicks_order: Optional[int]
    corners_and_indirect_freekicks_text: str
    direct_freekicks_order: Optional[int]
    direct_freekicks_text: str
    penalties_order: Optional[int]
    penalties_text: str
    expected_goals_per_90: float
    saves_per_90: float
    expected_assists_per_90: float
    expected_goal_involvements_per_90: float
    expected_goals_conceded_per_90: float
    goals_conceded_per_90: float
    now_cost_rank: int
    now_cost_rank_type: int
    form_rank: int
    form_rank_type: int
    points_per_game_rank: int
    points_per_game_rank_type: int
    selected_rank: int
    selected_rank_type: int
    starts_per_90: float
    clean_sheets_per_90: float

    player_team: Team = Relationship(back_populates="team_players")
    player_position: "ElementType" = Relationship(back_populates="players")
    player_history: List["PlayerHistory"] = Relationship(
        back_populates="player_profile"
    )

    @computed_field
    @property
    def goals_per_90(self) -> float:
        if self.minutes == 0:
            return 0
        return self.goals_scored / self.minutes * 90

    @computed_field
    @property
    def assists_per_90(self) -> float:
        if self.minutes == 0:
            return 0
        return self.assists / self.minutes * 90

    @computed_field
    @property
    def goal_involvements(self) -> int:
        return self.goals_scored + self.assists

    @computed_field
    @property
    def goal_involvements_per_90(self) -> float:
        if self.minutes == 0:
            return 0
        return self.goal_involvements / self.minutes * 90

    @computed_field
    @property
    def pct_of_team_pts(self) -> float:
        team = self.player_team.team_players

        team_total_pts = sum([p.total_points for p in team])

        return (
            round(self.total_points / team_total_pts * 100, 2)
            if team_total_pts > 0
            else 0
        )

    @computed_field
    @property
    def pct_of_team_goal_involvements(self) -> float:
        team = self.player_team.team_players

        team_total_goal_involvements = sum([p.goal_involvements for p in team])

        return (
            round(self.goal_involvements / team_total_goal_involvements * 100, 2)
            if team_total_goal_involvements > 0
            else 0
        )

    @computed_field
    @property
    def consistency_factor(self) -> float:
        matches = self.player_history
        std_pts = np.std([m.total_points for m in matches])
        mean_pts = np.mean([m.total_points for m in matches])

        return mean_pts / (std_pts + 10)

    @computed_field
    @property
    def points_adjusted_for_consistency(self) -> float:
        return self.total_points * (1 + self.consistency_factor)

    @computed_field
    @property
    def home_win_pct(self) -> float:
        games = self.player_history
        home_games = [g for g in games if g.was_home and g.minutes > 0]
        wins = [g for g in home_games if g.fixture_outcome == FixtureOutcome.WIN]

        return round(len(wins) / len(home_games) * 100, 2) if len(home_games) > 0 else 0

    @computed_field
    @property
    def away_win_pct(self) -> float:
        games = self.player_history
        away_games = [g for g in games if not g.was_home and g.minutes > 0]
        wins = [g for g in away_games if g.fixture_outcome == FixtureOutcome.WIN]

        return round(len(wins) / len(away_games) * 100, 2) if len(away_games) > 0 else 0

    @computed_field
    @property
    def home_stats(self) -> PlayerStats:
        return calculate_home_away_stats(
            self.player_history, is_home=True, per_90=False
        )

    @computed_field
    @property
    def home_stats_per_90(self) -> PlayerStats:
        return calculate_home_away_stats(self.player_history, is_home=True, per_90=True)

    @computed_field
    @property
    def away_stats(self) -> PlayerStats:
        return calculate_home_away_stats(
            self.player_history, is_home=False, per_90=False
        )

    @computed_field
    @property
    def away_stats_per_90(self) -> PlayerStats:
        return calculate_home_away_stats(
            self.player_history, is_home=False, per_90=True
        )


class ElementType(SQLModel, table=True):
    id: int = Field(primary_key=True)
    plural_name: str
    plural_name_short: str
    singular_name: str
    singular_name_short: str
    squad_select: int
    squad_min_play: int
    squad_max_play: int
    squad_min_select: Optional[int] = None
    squad_max_select: Optional[int] = None
    ui_shirt_specific: bool
    # sub_positions_locked: List[int] = Field(default_factory=list, sa_type=Column(JSON))
    element_count: int

    players: List["Element"] = Relationship(back_populates="player_position")


class ElementStat(SQLModel, table=False):
    name: str
    label: str


class Fixture(SQLModel, table=True):
    team_h: int
    team_a: int
    event: Optional[int]
    id: int = Field(primary_key=True)
    team_h_difficulty: int
    team_a_difficulty: int
    kickoff_time: str
    # stats: List[dict]
    team_a_score: Optional[int] = None
    team_h_score: Optional[int] = None
    pulse_id: int
    finished_provisional: bool
    minutes: int
    code: int
    finished: bool
    started: bool
    provisional_start_time: bool


class FixtureOutcome(Enum):
    WIN = 3
    LOSS = 0
    DRAW = 1


class PlayerHistory(SQLModel, table=True):
    element: int = Field(foreign_key="element.id")
    fixture: int
    opponent_team: int = Field(foreign_key="team.id")
    total_points: int
    was_home: bool
    kickoff_time: str
    team_h_score: Optional[int]
    team_a_score: Optional[int]
    round: int
    minutes: int
    goals_scored: int
    assists: int
    clean_sheets: int
    goals_conceded: int
    own_goals: int
    penalties_saved: int
    penalties_missed: int
    yellow_cards: int
    red_cards: int
    saves: int
    bonus: int
    bps: int
    influence: float
    creativity: float
    threat: float
    ict_index: float
    value: float
    transfers_balance: int
    selected: int
    transfers_in: int
    transfers_out: int
    expected_goal_involvements: float
    expected_goals: float
    expected_assists: float
    expected_goals_conceded: float
    starts: int

    # define a primary key based on element and fixture
    __table_args__ = (PrimaryKeyConstraint("element", "fixture"),)
    player_profile: "Element" = Relationship(back_populates="player_history")
    opponent: "Team" = Relationship(sa_relationship_kwargs={"uselist": False})

    @computed_field
    @property
    def fixture_outcome(self) -> str:
        if self.team_h_score == self.team_a_score:
            return FixtureOutcome.DRAW
        elif (self.team_h_score > self.team_a_score and self.was_home) or (
            self.team_h_score < self.team_a_score and not self.was_home
        ):
            return FixtureOutcome.WIN
        else:
            return FixtureOutcome.LOSS


class PlayerFixture(SQLModel, table=False):
    id: int
    code: int
    team_h: int
    team_h_score: Optional[int]
    team_a: int
    team_a_score: Optional[int]
    event: int
    finished: bool
    minutes: int
    provisional_start_time: bool
    kickoff_time: str
    event_name: str
    is_home: bool
    difficulty: int


class ManagerPick(SQLModel, table=False):
    element: int
    position: int
    multiplier: int
    is_captain: bool
    is_vice_captain: bool


class ManagerInfo(SQLModel, table=False):
    id: int
    joined_time: str
    started_event: int
    # events_entered: List
    favourite_team: int
    player_first_name: str
    player_last_name: str
    player_region_id: int
    player_region_name: str
    player_region_iso_code_short: str
    player_region_iso_code_long: str
    summary_overall_points: int
    summary_overall_rank: int
    summary_event_points: int
    summary_event_rank: int
    current_event: int
    name: str
    name_change_blocked: bool
    # leagues: dict
    last_deadline_bank: int
    last_deadline_value: int
    last_deadline_total_transfers: int
    years_active: int


class StaticData(SQLModel, table=False):
    events: List[Event]
    teams: List[Team]
    elements: List[Element]
    element_types: List[ElementType]
    element_stats: List[ElementStat]


class ManagerSquad(SQLModel, table=False):
    picks: List[ManagerPick]


def create_db_and_tables():
    db_filename = "fpl_dashboard.db"
    db_url = f"sqlite:///{db_filename}"

    engine = create_engine(db_url, echo=True)
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables()
