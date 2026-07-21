from datetime import datetime
from typing import Protocol
from uuid import uuid4

import pytest
from faker import Faker

from app.domain.entities.attack_record import AttackRecord
from app.domain.entities.target import Target
from app.domain.entities.tick import Tick
from app.domain.enums.attack import AttackResult, AttackType
from app.domain.values.database_id import DatabaseId


def random_string(faker: Faker, prefix: str = "") -> str:
    return f"{prefix}-{''.join(faker.random_letters())}"


class TargetFactory(Protocol):
    def __call__(
        self,
        *,
        id: DatabaseId = None,
        name: str | None = None,
        folder: str | None = None,
        file: str = "attacker.py",
        attacker_class: str | None = None,
        host: str | None = None,
        ports: list[int] | None = None,
        description: str | None = None,
    ) -> Target: ...


class AttackRecordFactory(Protocol):
    def __call__(
        self,
        *,
        target_id: DatabaseId = None,
        request_id: int | None = None,
        is_malicious: bool | None = None,
        tick_id: DatabaseId = None,
        team_id: DatabaseId = None,
        result: AttackResult | None = None,
    ) -> AttackRecord: ...


class TickFactory(Protocol):
    def __call__(
        self,
        *,
        id: DatabaseId = None,
        tick_num: int | None = None,
        timestamp: datetime | None = None,
    ) -> Tick: ...


@pytest.fixture(name="create_target")
def fixture_create_target(faker: Faker) -> TargetFactory:
    def _create_target(
        id: DatabaseId = None,
        name: str | None = None,
        folder: str | None = None,
        file: str = "attacker.py",
        attacker_class: str | None = None,
        host: str | None = None,
        ports: list[int] | None = None,
        description: str | None = None,
    ):
        name = name or random_string(faker, prefix="target-name")
        folder = folder or random_string(faker, prefix="target-folder")
        attacker_class = attacker_class or random_string(
            faker, prefix="target-attacker-class"
        )
        host = host or faker.ipv4_private()
        ports = ports or [faker.random_digit_not_null() for _ in range(3)]
        description = description or faker.sentence()

        return Target(
            id=id,
            name=name,
            folder=folder,
            file=file,
            attacker_class=attacker_class,
            host=host,
            ports=ports,
            description=description,
        )

    return _create_target


@pytest.fixture(name="create_attack_record")
def fixture_create_attack_record(
    existing_target: Target, faker: Faker
) -> AttackRecordFactory:
    def _determine_request_type(is_malicious: bool | None = None):
        if is_malicious is None:
            is_malicious = faker.boolean()

        if is_malicious:
            return AttackType.MALICIOUS
        else:
            return AttackType.BENIGN

    def _create_attack_record(
        target_id: DatabaseId = None,
        request_id: int | None = None,
        is_malicious: bool | None = None,
        tick_id: DatabaseId = None,
        team_id: DatabaseId = None,
        result: AttackResult | None = None,
    ) -> AttackRecord:
        target_id = target_id or existing_target.id
        request_type = AttackType.BENIGN
        if request_id is None:
            request_type = _determine_request_type(is_malicious)
            request_id = faker.random_digit_not_null() * request_type

        tick_id = tick_id or uuid4()
        team_id = team_id or uuid4()
        result = result or faker.random_element(AttackResult)

        return AttackRecord(
            target_id=target_id,
            request_id=request_id,
            tick_id=tick_id,
            team_id=team_id,
            result=result,
        )

    return _create_attack_record


@pytest.fixture(name="create_tick")
def fixture_create_tick(faker: Faker) -> TickFactory:
    def _create_tick(
        id: DatabaseId = None,
        tick_num: int | None = None,
        timestamp: datetime | None = None,
    ) -> Tick:

        if tick_num is None:
            tick_num = faker.random_digit_not_null()
        timestamp = timestamp or datetime.now()

        return Tick(id=id, tick_num=tick_num, timestamp=timestamp)

    return _create_tick


@pytest.fixture(name="new_target")
def fixture_new_target(create_target: TargetFactory):
    return create_target()


@pytest.fixture(name="target_id")
def fixture_target_id():
    return uuid4()


@pytest.fixture(name="existing_target")
def fixture_existing_target(create_target: TargetFactory, target_id: DatabaseId):
    return create_target(id=target_id)
