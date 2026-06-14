from enum import IntEnum

from pydantic import BaseModel
from sortedcontainers_pydantic import AnnotatedSortedDict

from app.schemas.target import TargetVulnInfo


class AttackResult(IntEnum):
    RESULT_SUCCESS = 1
    RESULT_DOWN = 0
    RESULT_FAILURE = -1


class AttackRecordInfo(TargetVulnInfo):
    tick: int
    team_id: int
    result: AttackResult


# TODO: Figure out how to work with this nicely as a schema
class AttackScheduleInfo(BaseModel):
    id: int | None = None

    target_id: int
    entries: AnnotatedSortedDict[int, list[TargetVulnInfo]]  # pyright: ignore

    def get_schedule_at_tick(self, tick: int) -> list[TargetVulnInfo]:
        return []
