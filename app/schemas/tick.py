from pydantic import BaseModel, Field

from app.schemas.attack import AttackRecord


class TickResults(BaseModel):
    team_id: int
    tick: int
    results: dict[int, list[AttackRecord]] = Field(default_factory=dict)
