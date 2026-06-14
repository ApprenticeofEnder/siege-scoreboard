from collections.abc import Generator

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel, create_engine

from app.models.schedule import TargetScheduleEntry
from app.models.target import Target
from app.models.team import Team
from app.models.tick import AttackRecordRow, TickSubmission
from app.repositories._helpers import require_id
from app.repositories.target import TargetRepository
from app.schemas.attack import AttackResult


@pytest.fixture
def session() -> Generator[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)
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

    target_repo = TargetRepository(session)
    target_dto = target_repo.get(0)
    assert target_dto is not None
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
        AttackRecordRow(
            tick_submission_id=require_id(submission),
            target_id=0,
            request_id=1,
            result=int(AttackResult.RESULT_SUCCESS),
        )
    )
    session.commit()

    session.add(
        AttackRecordRow(
            tick_submission_id=require_id(submission),
            target_id=0,
            request_id=1,
            result=int(AttackResult.RESULT_FAILURE),
        )
    )
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()
