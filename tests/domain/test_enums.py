from app.domain.enums.attack import AttackResult, AttackType


def test_attack_result():
    assert AttackResult.SUCCESS == 1
    assert AttackResult.DOWN == 0
    assert AttackResult.FAILURE == -1


def test_attack_type():
    assert AttackType.BENIGN == 1
    assert AttackType.MALICIOUS == -1
