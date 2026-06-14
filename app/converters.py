from collections import defaultdict
from datetime import UTC, datetime

from sqlmodel import Session, select

from app.models.tick import AttackRecord as AttackRecordRow
from app.models.tick import TickSubmission
from app.schemas.attack import AttackRecord, AttackResult
from app.schemas.tick import TickResults


def tick_results_to_submission(
    tick_results: TickResults,
    *,
    submitted_at: datetime | None = None,
) -> tuple[TickSubmission, list[AttackRecordRow]]:
    submission = TickSubmission(
        team_id=tick_results.team_id,
        tick=tick_results.tick,
        submitted_at=submitted_at or datetime.now(UTC),
    )
    records: list[AttackRecordRow] = []
    for target_id, attack_records in tick_results.results.items():
        for attack_record in attack_records:
            records.append(
                AttackRecordRow(
                    tick_submission_id=0,
                    target_id=target_id,
                    request_id=attack_record.request_id,
                    result=int(attack_record.result),
                )
            )
    return submission, records


def submission_to_tick_results(
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


def persist_tick_results(session: Session, tick_results: TickResults) -> TickSubmission:
    existing = session.exec(
        select(TickSubmission).where(
            TickSubmission.team_id == tick_results.team_id,
            TickSubmission.tick == tick_results.tick,
        )
    ).first()

    if existing is not None:
        for record in list(existing.attack_records):
            session.delete(record)
        submission = existing
        submission.submitted_at = datetime.now(UTC)
    else:
        submission, _ = tick_results_to_submission(tick_results)
        session.add(submission)
        session.flush()

    for target_id, attack_records in tick_results.results.items():
        for attack_record in attack_records:
            session.add(
                AttackRecordRow(
                    tick_submission_id=submission.id,  # type: ignore[arg-type]
                    target_id=target_id,
                    request_id=attack_record.request_id,
                    result=int(attack_record.result),
                )
            )

    session.commit()
    session.refresh(submission)
    return submission


def load_tick_results(session: Session, submission: TickSubmission) -> TickResults:
    records = session.exec(
        select(AttackRecordRow).where(
            AttackRecordRow.tick_submission_id == submission.id
        )
    ).all()
    return submission_to_tick_results(submission, list(records))
