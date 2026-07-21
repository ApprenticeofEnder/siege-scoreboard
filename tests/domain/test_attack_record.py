import pytest

from app.domain.enums.attack import AttackResult
from tests.domain.conftest import AttackRecordFactory


def test_service_down_points(create_attack_record: AttackRecordFactory):
    attack_record = create_attack_record(
        result=AttackResult.DOWN,
    )
    assert attack_record.points == -1


@pytest.mark.parametrize(
    "is_malicious,result,expected",
    [
        (False, AttackResult.SUCCESS, 1),  # benign success
        (False, AttackResult.FAILURE, -1),  # benign failure
        (True, AttackResult.SUCCESS, -1),  # malicious success
        (True, AttackResult.FAILURE, 1),  # malicious failure
    ],
)
def test_scoring(
    create_attack_record: AttackRecordFactory,
    is_malicious: bool,
    result: AttackResult,
    expected: int,
):
    attack_record = create_attack_record(is_malicious=is_malicious, result=result)
    assert attack_record.points == expected
