from pydantic import BaseModel, NegativeInt, PositiveInt, computed_field

from app.domain.enums.attack import AttackType
from app.domain.exceptions import ScheduleNotInitializedError, TargetNotPersistedError


class Target(BaseModel):
    id: PositiveInt | None = None
    name: str
    folder: str
    file: str
    attacker_class: str
    host: str
    ports: list[PositiveInt]
    description: str

    schedule: "AttackSchedule | None" = None

    def upsert_schedule_entry(self, tick: int, requests: list[int]) -> bool:
        if self.schedule is None:
            raise ScheduleNotInitializedError(
                "Target schedule must be initialized before upserting entries"
            )

        return self.schedule.upsert_entry(tick, requests)

    def init_schedule(self):
        if self.id is None:
            raise TargetNotPersistedError(
                "Target must have a valid database ID before initializing schedule"
            )
        self.schedule = AttackSchedule(target_id=self.id)


NonZeroInt = PositiveInt | NegativeInt


class TargetAttack(BaseModel):
    target_id: PositiveInt | None = None
    request_id: NonZeroInt
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


class AttackSchedule(BaseModel):
    id: PositiveInt | None = None

    target_id: PositiveInt | None = None
    entries: dict[int, list[TargetAttack]] = {}

    def upsert_entry(self, tick: int, requests: list[int]) -> bool:
        tick_exists = tick in self.entries
        is_inserted = not tick_exists

        attacks: list[TargetAttack] = [
            TargetAttack(target_id=self.target_id, request_id=request_id)
            for request_id in requests
        ]

        self.entries[tick] = attacks

        return is_inserted

    def at_tick(self, current_tick: int) -> list[TargetAttack] | None:
        if current_tick < 0:
            return None
        applicable = [t for t in self.entries if t <= current_tick]
        if not applicable:
            return None
        return self.entries[max(applicable)]
