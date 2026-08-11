from functools import cached_property

from pydantic import BaseModel, NegativeInt, PositiveInt, computed_field

from app.domain.enums import AttackType
from app.domain.exceptions import ScheduleNotInitializedError, TargetNotPersistedError
from app.domain.values.database_id import DatabaseId


class Target(BaseModel):
    id: DatabaseId | None = None
    name: str
    folder: str
    file: str
    attacker_class: str
    host: str
    ports: list[PositiveInt]
    description: str

    schedule: "AttackSchedule | None" = None

    def upsert_schedule_entries(self, entries: dict[int, list[int]]) -> dict[int, bool]:
        result = {
            tick: self.upsert_schedule_entry(tick, requests)
            for tick, requests in entries.items()
        }
        return result
    @computed_field
    @cached_property
    def vulns(self) -> int | None:
        pass

    def upsert_schedule(self, entries: dict[int, list[int]]) -> int:
        """
        Creates or updates the attack schedule.
        """
        entries_inserted: list[bool] = []
        inserted = False
        for tick, entry in entries.items():
            entries_inserted.append(self.upsert_schedule_entry(tick, entry))

        return inserted

    def upsert_schedule_entry(self, tick: int, requests: list[int]) -> bool:
        if self.schedule is None:
            raise ScheduleNotInitializedError(
                "Target schedule must be initialized before upserting entries"
            )

        return self.schedule.upsert_entry(tick, requests)

    def init_schedule(self, entries: dict[int, list[int]] | None = None) -> int | None:
        if self.id is None:
            raise TargetNotPersistedError(
                "Target must have a valid database ID before initializing schedule"
            )
        self.schedule = AttackSchedule(target_id=self.id)

        if entries is None:
            return None

        return self.upsert_schedule(entries)

    def at_tick(self, tick: int) -> list["TargetAttack"] | None:
        if self.schedule is None:
            raise ScheduleNotInitializedError(
                "Target schedule must be initialized before obtaining attack lists"
            )

        return self.schedule.at_tick(tick)


NonZeroInt = PositiveInt | NegativeInt


class TargetAttack(BaseModel):
    target_id: DatabaseId | None = None
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
    id: DatabaseId | None = None

    target_id: DatabaseId | None = None
    entries: dict[int, list[TargetAttack]] = {}

    def upsert_entries(self, entries: dict[int, list[int]]) -> dict[int, bool]:
        result = {
            tick: self.upsert_entry(tick, requests)
            for tick, requests in entries.items()
        }
        return result

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
