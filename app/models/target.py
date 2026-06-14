from sqlalchemy import UniqueConstraint
from sqlmodel import Constraint, Field, SQLModel


class Target(SQLModel, table=True):
    __tablename__: str = "targets"

    id: int | None = Field(default=None, primary_key=True)
    name: str
    folder: str
    file: str
    attacker_class: str
    address: str
    description: str
    vulns: int
    req_per_tick: int


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
