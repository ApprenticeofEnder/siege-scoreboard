from typing import Annotated

from pydantic import BaseModel, BeforeValidator, PositiveInt, computed_field

from app.domain.enums.attack import AttackType


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
