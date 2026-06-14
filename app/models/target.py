from collections import defaultdict
from collections.abc import Sequence
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.schemas import TargetDTO

if TYPE_CHECKING:
    from app.models.schedule import TargetScheduleEntry
    from app.models.tick import AttackRecordRow


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
    attack_records: list["AttackRecord"] = Relationship(back_populates="target")

    def to_dto(self, schedule_entries: Sequence["TargetScheduleEntry"]) -> TargetDTO:
        assert self.id is not None
        schedule: dict[int, list[int]] = defaultdict(list)
        for entry in schedule_entries:
            schedule[entry.tick].append(entry.request_id)
        for tick in schedule:
            schedule[tick].sort()

        return TargetDTO(
            **self.model_dump(exclude={"schedule_entries", "attack_records"}),
            schedule=schedule,
        )
