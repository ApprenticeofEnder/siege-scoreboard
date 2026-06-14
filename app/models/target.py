from sqlmodel import Constraint, Field, PrimaryKeyConstraint

from app.models.base import BaseDbModel, BaseDbModelWithId


class Target(BaseDbModelWithId, table=True):
    __tablename__: str = "targets"

    name: str
    folder: str
    file: str
    attacker_class: str
    address: str
    description: str
    req_per_tick: int


class TargetVuln(BaseDbModel, table=True):
    __tablename__: str = "target_vulns"
    __table_args__: tuple[Constraint] = (
        PrimaryKeyConstraint("target_id", "request_id", name="pk_target_vulns"),
    )

    target_id: int = Field(foreign_key="targets.id")
    request_id: int
