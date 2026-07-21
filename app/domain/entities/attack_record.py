from pydantic import computed_field

from app.domain.entities.target import TargetAttack
from app.domain.enums.attack import AttackResult
from app.domain.values.database_id import NonNullDatabaseId


class AttackRecord(TargetAttack):
    tick_id: NonNullDatabaseId
    team_id: NonNullDatabaseId
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
