from typing import Protocol, TypeVar

from app.domain.entities.attack_record import AttackRecord
from app.domain.entities.target import AttackSchedule, Target, TargetAttack
from app.domain.entities.team import Team
from app.domain.entities.tick import Tick

T = TypeVar("T", AttackRecord, AttackSchedule, Target, TargetAttack, Tick, Team)


class IEntityRepository[T](Protocol):
    async def upsert(self, target: T) -> T: ...

    async def get_by_id(self, id: int) -> T | None: ...

    async def list_all(self) -> list[T]: ...

    async def delete_by_id(self, id: int) -> bool: ...
