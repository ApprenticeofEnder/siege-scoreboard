from enum import IntEnum


class AttackResult(IntEnum):
    SUCCESS = 1
    DOWN = 0
    FAILURE = -1


class AttackType(IntEnum):
    BENIGN = 1
    MALICIOUS = -1
