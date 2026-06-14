from collections.abc import Generator
from typing import Any

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, create_engine, select

from app.converters import (
    load_tick_results,
    persist_tick_results,
)
from app.models.schedule import TargetScheduleEntry
from app.models.target import Target
from app.models.team import Team
from app.models.tick import AttackRecord, TickSubmission
from app.schemas.attack import AttackRecord as AttackRecordSchema
from app.schemas.attack import AttackResult
from app.schemas.tick import TickResults


@pytest.fixture
def session() -> Generator[Session, Any]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
    )
    with Session(engine) as session:
        yield session


def test_team_and_target_relationships(session: Session) -> None:
    team = Team(id=0, name="Alpha", bot_signing_key_pem="pem-alpha")
    target = Target(
        id=0,
        name="WebVault",
        folder="webvault",
        file="attacker.py",
        attacker_class="WebVaultAttacker",
        address="127.0.0.1:5001",
        description="Test service",
        vulns=2,
        req_per_tick=4,
    )
    schedule_entry = TargetScheduleEntry(target_id=0, tick=0, request_id=1)

    session.add(team)
    session.add(target)
    session.add(schedule_entry)
    session.commit()

    loaded_team = session.get(Team, 0)
    loaded_target = session.get(Target, 0)
    assert loaded_team is not None
    assert loaded_target is not None

    team_dto = loaded_team.to_dto()
    assert team_dto.name == "Alpha"

    target_dto = loaded_target.to_dto(
        session.exec(
            select(TargetScheduleEntry).where(TargetScheduleEntry.target_id == 0)
        ).all(),
    )
    assert target_dto.schedule == {0: [1]}


def test_tick_submission_unique_constraint(session: Session) -> None:
    session.add(Team(id=0, name="Alpha", bot_signing_key_pem="pem-alpha"))
    session.commit()

    session.add(TickSubmission(team_id=0, tick=1))
    session.commit()

    session.add(TickSubmission(team_id=0, tick=1))
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_attack_record_unique_constraint(session: Session) -> None:
    session.add(Team(id=0, name="Alpha", bot_signing_key_pem="pem-alpha"))
    session.add(
        Target(
            id=0,
            name="WebVault",
            folder="webvault",
            file="attacker.py",
            attacker_class="WebVaultAttacker",
            address="127.0.0.1:5001",
            description="Test service",
            vulns=2,
            req_per_tick=4,
        )
    )
    session.commit()

    submission = TickSubmission(team_id=0, tick=1)
    session.add(submission)
    session.commit()
    session.refresh(submission)

    session.add(
        AttackRecord(
            tick_submission_id=submission.id,  # type: ignore[arg-type]
            target_id=0,
            request_id=1,
            result=int(AttackResult.RESULT_SUCCESS),
        )
    )
    session.commit()

    session.add(
        AttackRecord(
            tick_submission_id=submission.id,  # type: ignore[arg-type]
            target_id=0,
            request_id=1,
            result=int(AttackResult.RESULT_FAILURE),
        )
    )
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def test_tick_results_round_trip(session: Session) -> None:
    session.add(Team(id=0, name="Alpha", bot_signing_key_pem="pem-alpha"))
    session.add(
        Target(
            id=0,
            name="WebVault",
            folder="webvault",
            file="attacker.py",
            attacker_class="WebVaultAttacker",
            address="127.0.0.1:5001",
            description="Test service",
            vulns=2,
            req_per_tick=4,
        )
    )
    session.commit()

    original = TickResults(
        team_id=0,
        tick=3,
        results={
            0: [
                AttackRecordSchema(request_id=1, result=AttackResult.RESULT_SUCCESS),
                AttackRecordSchema(request_id=-1, result=AttackResult.RESULT_FAILURE),
            ]
        },
    )

    submission = persist_tick_results(session, original)
    round_tripped = load_tick_results(session, submission)

    assert round_tripped.team_id == original.team_id
    assert round_tripped.tick == original.tick
    assert set(round_tripped.results.keys()) == set(original.results.keys())
    for target_id in original.results:
        expected = sorted(
            original.results[target_id], key=lambda record: record.request_id
        )
        actual = sorted(
            round_tripped.results[target_id], key=lambda record: record.request_id
        )
        assert actual == expected
