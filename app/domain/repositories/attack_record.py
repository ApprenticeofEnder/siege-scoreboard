from abc import ABCMeta

from app.domain.entities.attack_record import AttackRecord
from app.domain.repositories.entity_repository import IEntityRepository
from app.domain.values.database_id import DatabaseId


class IAttackRecordRepository(IEntityRepository[AttackRecord], metaclass=ABCMeta):
    async def list_for_team(self, team_id: DatabaseId) -> list[AttackRecord]: ...

    async def list_for_target(self, target_id: DatabaseId) -> list[AttackRecord]: ...

    async def get_by_target_and_team(
        self, target_id: DatabaseId, team_id: DatabaseId
    ) -> AttackRecord | None: ...

    async def list_for_tick(self, tick_id: DatabaseId) -> list[AttackRecord]: ...

    async def list_malicious_for_tick(
        self, tick_id: DatabaseId
    ) -> list[AttackRecord]: ...

    async def list_benign_for_tick(self, tick_id: DatabaseId) -> list[AttackRecord]: ...
