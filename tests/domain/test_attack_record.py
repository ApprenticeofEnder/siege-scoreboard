from app.domain.enums.attack import AttackResult
from tests.domain.conftest import AttackRecordFactory


def test_service_down_points(create_attack_record: AttackRecordFactory):
    attack_record = create_attack_record(
        result=AttackResult.DOWN,
    )
    assert attack_record.points == -1


def test_benign_success_points(create_attack_record: AttackRecordFactory):
    attack_record = create_attack_record(
        is_malicious=False, result=AttackResult.SUCCESS
    )
    assert attack_record.points == 1


def test_malicious_success_points(create_attack_record: AttackRecordFactory):
    attack_record = create_attack_record(is_malicious=True, result=AttackResult.SUCCESS)
    assert attack_record.points == -1


def test_malicious_failure_points(create_attack_record: AttackRecordFactory):
    attack_record = create_attack_record(is_malicious=True, result=AttackResult.FAILURE)
    assert attack_record.points == 1


def test_benign_failure_points(create_attack_record: AttackRecordFactory):
    attack_record = create_attack_record(
        is_malicious=False, result=AttackResult.FAILURE
    )
    assert attack_record.points == -1
