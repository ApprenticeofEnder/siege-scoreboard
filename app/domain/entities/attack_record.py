from pydantic import PositiveInt, computed_field

from app.domain.entities.target import TargetAttack
from app.domain.enums.attack import AttackResult


class AttackRecord(TargetAttack):
    tick_id: PositiveInt
    team_id: PositiveInt
    result: AttackResult
    """Did the attack succeed, fail, or was the service down?"""

    @computed_field
    @property
    def points(self) -> int:
        """
        Points for this attack.

        Potential values:
          - DOWN = -1
          - SUCCESS (1) * BENIGN (1) = 1
          - SUCCESS (1) * MALICIOUS (-1) = -1
          - FAILURE (-1) * BENIGN (1) = -1
          - FAILURE (-1) * MALICIOUS (-1) = 1
        """
        if self.result == AttackResult.DOWN:
            return -1

        return self.result * self.attack_type
