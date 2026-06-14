# pyright: reportUndefinedVariable=false

from sqlmodel import Field, Relationship, SQLModel


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

    schedule_entries: list["TargetScheduleEntry"] = Relationship(
        back_populates="target"
    )
    attack_records: list["AttackRecordRow"] = Relationship(back_populates="target")
