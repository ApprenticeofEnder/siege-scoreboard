from collections import defaultdict
from collections.abc import Sequence
from typing import Protocol

from app.models.schedule import TargetScheduleEntry
from app.models.target import Target
from app.models.team import Team
from app.models.tick import AttackRecordRow, TickSubmission
from app.schemas.attack import AttackRecord, AttackResult
from app.schemas.target import TargetDTO
from app.schemas.team import TeamDTO
from app.schemas.tick import TickResults


class HasOptionalId(Protocol):
    id: int | None


def require_id(entity: HasOptionalId) -> int:
    if entity.id is None:
        msg = "Expected persisted row with a primary key"
        raise ValueError(msg)
    return entity.id


def team_to_dto(team: Team) -> TeamDTO:
    return TeamDTO(
        id=require_id(team),
        name=team.name,
        email=team.email,
        bot_signing_key_pem=team.bot_signing_key_pem,
    )


def target_to_dto(
    target: Target, schedule_entries: Sequence[TargetScheduleEntry]
) -> TargetDTO:
    schedule: dict[int, list[int]] = defaultdict(list)
    for entry in schedule_entries:
        schedule[entry.tick].append(entry.request_id)
    for tick in schedule:
        schedule[tick].sort()

    return TargetDTO(
        id=require_id(target),
        name=target.name,
        folder=target.folder,
        file=target.file,
        attacker_class=target.attacker_class,
        address=target.address,
        description=target.description,
        vulns=target.vulns,
        req_per_tick=target.req_per_tick,
        schedule=dict(schedule),
    )


def attack_record_rows(
    submission_id: int, tick_results: TickResults
) -> list[AttackRecordRow]:
    rows: list[AttackRecordRow] = []
    for target_id, attack_records in tick_results.results.items():
        for attack_record in attack_records:
            rows.append(
                AttackRecordRow(
                    tick_submission_id=submission_id,
                    target_id=target_id,
                    request_id=attack_record.request_id,
                    result=int(attack_record.result),
                )
            )
    return rows


def tick_results_from_submission(
    submission: TickSubmission, records: list[AttackRecordRow]
) -> TickResults:
    results: dict[int, list[AttackRecord]] = defaultdict(list)
    for record in records:
        results[record.target_id].append(
            AttackRecord(
                request_id=record.request_id,
                result=AttackResult(record.result),
            )
        )
    for target_id in results:
        results[target_id].sort(key=lambda item: item.request_id)
    return TickResults(
        team_id=submission.team_id,
        tick=submission.tick,
        results=dict(results),
    )
