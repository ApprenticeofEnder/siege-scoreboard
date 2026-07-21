from abc import ABCMeta

from app.domain.entities.attack_record import AttackRecord
from app.domain.repositories.entity_repository import IEntityRepository
from app.domain.values.database_id import DatabaseId
from app.models.attacks import AttackSchedule


class IAttackScheduleRepository(IEntityRepository[AttackSchedule], metaclass=ABCMeta):
    async def list_for_team(self, team_id: DatabaseId) -> list[AttackSchedule]: ...

    async def list_for_target(self, target_id: DatabaseId) -> list[AttackSchedule]: ...

    async def get_by_target_and_team(
        self, target_id: DatabaseId, team_id: DatabaseId
    ) -> AttackRecord | None: ...
