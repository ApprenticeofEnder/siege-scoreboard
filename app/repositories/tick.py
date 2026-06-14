from datetime import UTC, datetime

from sqlmodel import Session, col, delete, select

from app.models.tick import AttackRecordRow, TickSubmission
from app.repositories._helpers import (
    attack_record_rows,
    require_id,
    tick_results_from_submission,
)
from app.schemas.tick import TickResults


class TickSubmissionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def upsert(self, tick_results: TickResults) -> TickResults:
        existing = self._session.exec(
            select(TickSubmission).where(
                TickSubmission.team_id == tick_results.team_id,
                TickSubmission.tick == tick_results.tick,
            )
        ).first()

        if existing is not None:
            submission = existing
            submission.submitted_at = datetime.now(UTC)
            self._session.exec(
                delete(AttackRecordRow).where(
                    col(AttackRecordRow.tick_submission_id) == require_id(submission)
                )
            )
        else:
            submission = TickSubmission(
                team_id=tick_results.team_id,
                tick=tick_results.tick,
                submitted_at=datetime.now(UTC),
            )
            self._session.add(submission)
            self._session.flush()

        for row in attack_record_rows(require_id(submission), tick_results):
            self._session.add(row)

        self._session.flush()
        records = self._session.exec(
            select(AttackRecordRow).where(
                col(AttackRecordRow.tick_submission_id) == require_id(submission)
            )
        ).all()
        return tick_results_from_submission(submission, list(records))

    def get_by_team_tick(self, team_id: int, tick: int) -> TickResults | None:
        submission = self._session.exec(
            select(TickSubmission).where(
                TickSubmission.team_id == team_id,
                TickSubmission.tick == tick,
            )
        ).first()
        if submission is None:
            return None

        records = self._session.exec(
            select(AttackRecordRow).where(
                col(AttackRecordRow.tick_submission_id) == require_id(submission)
            )
        ).all()
        return tick_results_from_submission(submission, list(records))
