from enum import IntEnum

from pydantic import BaseModel


class AttackResult(IntEnum):
    RESULT_SUCCESS = 1
    RESULT_DOWN = 0
    RESULT_FAILURE = -1


class AttackRecord(BaseModel):
    request_id: int
    result: AttackResult

    @classmethod
    def from_pair(cls, pair: list[int]) -> "AttackRecord":
        request_id, result_value = pair
        return cls(request_id=request_id, result=AttackResult(result_value))
