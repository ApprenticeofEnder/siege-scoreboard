from pydantic import BaseModel, PositiveInt

from app.domain.entities.target import TargetAttack


class AttackSchedule(BaseModel):
    id: PositiveInt | None = None

    target_id: PositiveInt | None = None
    entries: dict[int, list[TargetAttack]]
