import pytest
from faker import Faker
from pydantic import ValidationError

from app.domain.entities.target import AttackSchedule, Target, TargetAttack
from app.domain.enums.attack import AttackType
from app.domain.exceptions import ScheduleNotInitializedError, TargetNotPersistedError
from tests.domain.conftest import TargetFactory


def test_target_creation(new_target: Target):
    assert new_target.id is None
    assert new_target.schedule is None


def test_target_port_validation(create_target: TargetFactory):
    with pytest.raises(ValidationError):
        _ = create_target(ports=[-1, 3000])


def test_existing_target(existing_target: Target, target_id: int):
    assert existing_target.id == target_id


def test_benign_target_attack(existing_target: Target, faker: Faker):
    request_id = faker.random_digit_not_null()
    attack = TargetAttack(target_id=existing_target.id, request_id=request_id)

    assert attack.attack_type == AttackType.BENIGN


def test_malicious_target_attack(existing_target: Target, faker: Faker):
    request_id = faker.random_digit_not_null() * -1
    attack = TargetAttack(target_id=existing_target.id, request_id=request_id)
    assert attack.attack_type == AttackType.MALICIOUS


def test_non_persisted_target_attack(new_target: Target, faker: Faker):
    request_id = faker.random_digit_not_null() * -1
    attack = TargetAttack(target_id=new_target.id, request_id=request_id)
    assert attack.attack_type == AttackType.MALICIOUS
    assert attack.target_id is None

    request_id = faker.random_digit_not_null()
    attack = TargetAttack(target_id=new_target.id, request_id=request_id)
    assert attack.attack_type == AttackType.BENIGN
    assert attack.target_id is None


def test_init_schedule_change(existing_target: Target):
    assert existing_target.schedule is None

    existing_target.init_schedule()

    assert existing_target.schedule is not None


def test_init_schedule_target_id(existing_target: Target):
    existing_target.init_schedule()

    assert existing_target.schedule is not None

    assert existing_target.schedule.target_id == existing_target.id


def test_schedule_upsert(existing_target: Target):
    existing_target.init_schedule()

    assert existing_target.schedule is not None
    assert len(existing_target.schedule.entries) == 0

    request_ids: list[int] = [1, 2, -1, -2]

    assert existing_target.upsert_schedule_entry(1, request_ids)

    scheduled_attacks = existing_target.schedule.at_tick(1)
    assert scheduled_attacks is not None

    for attack, request_id in zip(scheduled_attacks, request_ids):
        assert attack.target_id == existing_target.id
        if request_id > 0:
            assert attack.attack_type == AttackType.BENIGN
        else:
            assert attack.attack_type == AttackType.MALICIOUS


def test_at_tick_sparse_gte(existing_target: Target):
    existing_target.init_schedule()
    assert existing_target.schedule is not None

    existing_target.upsert_schedule_entry(1, [1, 2])
    existing_target.upsert_schedule_entry(5, [3, 4])

    tick_one_attacks = existing_target.schedule.at_tick(3)
    assert tick_one_attacks is not None
    assert [attack.request_id for attack in tick_one_attacks] == [1, 2]

    tick_five_attacks = existing_target.schedule.at_tick(6)
    assert tick_five_attacks is not None
    assert [attack.request_id for attack in tick_five_attacks] == [3, 4]

    assert existing_target.schedule.at_tick(0) is None


def test_at_tick_insertion_order_independent(existing_target: Target):
    existing_target.init_schedule()
    assert existing_target.schedule is not None

    schedule_first = AttackSchedule(target_id=existing_target.id)
    schedule_first.upsert_entry(5, [3, 4])
    schedule_first.upsert_entry(1, [1, 2])

    schedule_second = AttackSchedule(target_id=existing_target.id)
    schedule_second.upsert_entry(1, [1, 2])
    schedule_second.upsert_entry(5, [3, 4])

    first_attacks = schedule_first.at_tick(6)
    second_attacks = schedule_second.at_tick(6)

    assert first_attacks is not None
    assert second_attacks is not None
    assert [attack.request_id for attack in first_attacks] == [3, 4]
    assert [attack.request_id for attack in second_attacks] == [3, 4]


def test_upsert_overwrite_returns_false(existing_target: Target):
    existing_target.init_schedule()

    assert existing_target.upsert_schedule_entry(1, [1, 2])
    assert not existing_target.upsert_schedule_entry(1, [3, 4])


def test_upsert_without_schedule_raises(new_target: Target):
    with pytest.raises(ScheduleNotInitializedError):
        new_target.upsert_schedule_entry(1, [1, 2])


def test_init_schedule_without_id_raises(new_target: Target):
    with pytest.raises(TargetNotPersistedError):
        new_target.init_schedule()
