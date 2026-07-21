from abc import ABCMeta

from app.domain.entities.target import AttackSchedule, Target
from app.domain.repositories.entity_repository import IEntityRepository
from app.domain.values.database_id import DatabaseId


class ITargetRepository(IEntityRepository[Target], metaclass=ABCMeta):
    async def list_for_team(self, team_id: DatabaseId) -> list[Target]: ...

    async def get_schedule(self, target_id: DatabaseId) -> AttackSchedule: ...
