from datetime import datetime

from sqlalchemy import UniqueConstraint
from sqlmodel import Constraint, Field, SQLModel


class TickSubmission(SQLModel, table=True):
    __tablename__: str = "tick_submissions"
    __table_args__: tuple[Constraint] = (
        UniqueConstraint("team_id", "tick", name="uq_tick_submissions_team_tick"),
    )

    id: int | None = Field(default=None, primary_key=True)
    team_id: int = Field(foreign_key="teams.id")
    tick: int
    submitted_at: datetime | None = None


class AttackRecordRow(SQLModel, table=True):
    __tablename__: str = "attack_records"
    __table_args__: tuple[UniqueConstraint] = (
        UniqueConstraint(
            "tick_submission_id",
            "target_id",
            "request_id",
            name="uq_attack_records_submission_target_request",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    tick_submission_id: int = Field(foreign_key="tick_submissions.id")
    target_id: int = Field(foreign_key="targets.id")
    request_id: int
    result: int
