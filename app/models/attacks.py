from datetime import datetime

from sqlalchemy import UniqueConstraint
from sqlmodel import Constraint, Field, ForeignKeyConstraint

from app.models.base import BaseDbModelWithId
from app.schemas.target import AttackResult


class AttackSchedule(BaseDbModelWithId, table=True):
    __tablename__: str = "attack_schedules"

    target_id: int = Field(foreign_key="target.id")


class AttackScheduleEntry(BaseDbModelWithId, table=True):
    __tablename__: str = "attack_schedule_entries"
    __table_args__: tuple[Constraint, ...] = (
        UniqueConstraint(
            "schedule_id",
            "target_id",
            "request_id",
            "start_tick",
            name="uq_attack_schedules",
        ),
        ForeignKeyConstraint(
            ["target_id", "request_id"],
            ["target_vulns.target_id", "target_vulns.request_id"],
        ),
    )

    schedule_id: int = Field(foreign_key="attack_schedules.id")
    target_id: int
    request_id: int
    start_tick: int
    request_count: int


class AttackRecord(BaseDbModelWithId, table=True):
    __tablename__: str = "attack_records"
    __table_args__: tuple[Constraint, ...] = (
        UniqueConstraint(
            "team_id",
            "tick",
            "target_id",
            "request_id",
            name="uq_tick_submissions",
        ),
        ForeignKeyConstraint(
            ["target_id", "request_id"],
            ["target_vulns.target_id", "target_vulns.request_id"],
        ),
    )

    # keep-sorted start
    request_id: int
    result: AttackResult
    target_id: int
    team_id: int = Field(foreign_key="teams.id")
    tick: int
    # keep-sorted end

    submitted_at: datetime | None = Field(default=None)
