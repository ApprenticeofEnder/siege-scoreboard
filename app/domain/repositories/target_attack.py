from abc import ABCMeta

from app.domain.entities.target import TargetAttack
from app.domain.repositories.entity_repository import IEntityRepository
from app.domain.values.database_id import DatabaseId


class ITargetAttackRespository(IEntityRepository[TargetAttack], metaclass=ABCMeta):
    async def list_for_target(self, target_id: DatabaseId) -> list[TargetAttack]: ...

    async def list_malicious_for_target(
        self, target_id: DatabaseId
    ) -> list[TargetAttack]: ...
