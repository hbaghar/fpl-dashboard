from sqlmodel import SQLModel, Field, Column, JSON, PrimaryKeyConstraint, create_engine, Relationship
from pydantic import computed_field
from typing import List, Optional

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

class Element(SQLModel, table=True):
    chance_of_playing_next_round: Optional[int]
    chance_of_playing_this_round: Optional[int]
    code: int
    cost_change_event: int
    cost_change_event_fall: int
    cost_change_start: int
    cost_change_start_fall: int
    dreamteam_count: int
    element_type: int = Field(foreign_key='elementtype.id')
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
    team: int = Field(foreign_key='team.id')
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
    player_history: List["PlayerHistory"] = Relationship(back_populates="player_profile")

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
    def goal_involvements_per_90(self) -> float:
        if self.minutes == 0:
            return 0
        return (self.goals_scored + self.assists) / self.minutes * 90

class ElementType(SQLModel, table=True):
    id: int = Field(primary_key=True)
    plural_name: str
    plural_name_short: str
    singular_name: str
    singular_name_short: str
    squad_select: int
    squad_min_play: int
    squad_max_play: int
    squad_min_select: Optional[int]=None
    squad_max_select: Optional[int]=None
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

class PlayerHistory(SQLModel, table=True):
    element: int = Field(foreign_key='element.id')
    fixture: int
    opponent_team: int = Field(foreign_key='team.id')
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
    __table_args__ = (PrimaryKeyConstraint('element', 'fixture'),)
    player_profile: "Element" = Relationship(back_populates="player_history")

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