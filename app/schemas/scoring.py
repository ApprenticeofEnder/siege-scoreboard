from pydantic import BaseModel, Field


class TargetScore(BaseModel):
    empty_result: bool = False
    benign_successes: int = 0
    benign_failures: int = 0
    malicious_successes: int = 0
    malicious_failures: int = 0
    service_down_count: int = 0
    ignored_benign_successes: int = 0
    ignored_malicious_failures: int = 0
    caps_reached: int = 0
    score_delta: int = 0


class PreparedScore(BaseModel):
    tick: int
    tick_score: int
    tick_since: int
    target_scores: dict[int, TargetScore] = Field(default_factory=dict)


class TimestampedScore(BaseModel):
    time: int  # UNIX epoch
    score: int


class TeamScore(TimestampedScore):
    tick: int
    details: dict[int, TargetScore] = Field(default_factory=dict)


class CompetitionScore(BaseModel):
    place: int
    team_id: int
    team_name: str
    score: int


class ChartScore(TimestampedScore):
    team_id: int
