from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import Constraint, Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.target import Target


class TargetScheduleEntry(SQLModel, table=True):
    __tablename__: str = "target_schedule_entries"
    __table_args__: tuple[Constraint] = (
        UniqueConstraint(
            "target_id",
            "tick",
            "request_id",
            name="uq_target_schedule_entries_target_tick_request",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    target_id: int = Field(foreign_key="targets.id")
    tick: int
    request_id: int

    target: "Target" = Relationship(back_populates="schedule_entries")
