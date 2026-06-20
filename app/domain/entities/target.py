from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, PositiveInt, computed_field

from app.domain.entities.attack_schedule import AttackSchedule
from app.domain.enums.attack import AttackType


class Target(BaseModel):
    id: PositiveInt | None = None
    name: str
    folder: str
    file: str
    attacker_class: str
    host: str
    ports: list[PositiveInt]
    description: str
    vulns: PositiveInt
    req_per_tick: PositiveInt

    schedule: AttackSchedule | None = None

    @classmethod
    def from_yaml(cls, yaml_record: dict[str, Any]):
        schedule: dict[int, list[int]] = yaml_record.pop("schedule", {})


class TargetAttack(BaseModel):
    target_id: PositiveInt
    request_id: Annotated[int, BeforeValidator(lambda id: id != 0)]
    """
    ID of the request (attack) to be sent. 

    Benign requests are positive, malicious requests are negative.
    """

    @computed_field
    @property
    def attack_type(self) -> AttackType:
        if self.request_id > 0:
            return AttackType.BENIGN
        return AttackType.MALICIOUS
