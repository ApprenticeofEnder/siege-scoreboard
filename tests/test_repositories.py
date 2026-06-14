from collections.abc import Generator

import pytest
from sqlmodel import Session, SQLModel, create_engine

from app.schemas.attack import AttackRecord, AttackResult
from app.schemas.target import TargetDTO
from app.schemas.team import TeamDTO
from app.schemas.tick import TickResults
from app.unit_of_work import unit_of_work


@pytest.fixture
def session() -> Generator[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_team_upsert_and_get(session: Session) -> None:
    team = TeamDTO(
        id=0,
        name="Alpha",
        email="alpha@example.com",
        bot_signing_key_pem="pem",
    )

    with unit_of_work(session=session) as uow:
        uow.teams.upsert(team)

    with unit_of_work(session=session) as uow:
        loaded = uow.teams.get(0)

    assert loaded == team


def test_target_upsert_get_and_list_all(session: Session) -> None:
    target = TargetDTO(
        id=0,
        name="WebVault",
        folder="webvault",
        file="attacker.py",
        attacker_class="WebVaultAttacker",
        address="127.0.0.1:5001",
        description="Test service",
        vulns=2,
        req_per_tick=4,
        schedule={0: [1, 2], 1: [-1]},
    )

    with unit_of_work(session=session) as uow:
        uow.targets.upsert(target)

    with unit_of_work(session=session) as uow:
        loaded = uow.targets.get(0)
        all_targets = uow.targets.list_all()

    assert loaded == target
    assert all_targets == [target]


def test_tick_results_upsert_and_get(session: Session) -> None:
    with unit_of_work(session=session) as uow:
        uow.teams.upsert(TeamDTO(id=0, name="Alpha", bot_signing_key_pem="pem"))
        uow.targets.upsert(
            TargetDTO(
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

    original = TickResults(
        team_id=0,
        tick=3,
        results={
            0: [
                AttackRecord(request_id=1, result=AttackResult.RESULT_SUCCESS),
                AttackRecord(request_id=-1, result=AttackResult.RESULT_FAILURE),
            ]
        },
    )

    with unit_of_work(session=session) as uow:
        uow.ticks.upsert(original)

    with unit_of_work(session=session) as uow:
        loaded = uow.ticks.get_by_team_tick(team_id=0, tick=3)

    assert loaded is not None
    assert loaded.team_id == original.team_id
    assert loaded.tick == original.tick
    for target_id, records in original.results.items():
        assert sorted(loaded.results[target_id], key=lambda r: r.request_id) == sorted(
            records, key=lambda r: r.request_id
        )


def test_tick_results_upsert_overwrites(session: Session) -> None:
    with unit_of_work(session=session) as uow:
        uow.teams.upsert(TeamDTO(id=0, name="Alpha", bot_signing_key_pem="pem"))
        uow.targets.upsert(
            TargetDTO(
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

    initial = TickResults(
        team_id=0,
        tick=1,
        results={
            0: [AttackRecord(request_id=1, result=AttackResult.RESULT_SUCCESS)]
        },
    )
    updated = TickResults(
        team_id=0,
        tick=1,
        results={
            0: [AttackRecord(request_id=2, result=AttackResult.RESULT_FAILURE)]
        },
    )

    with unit_of_work(session=session) as uow:
        uow.ticks.upsert(initial)
        uow.ticks.upsert(updated)

    with unit_of_work(session=session) as uow:
        loaded = uow.ticks.get_by_team_tick(team_id=0, tick=1)

    assert loaded == updated
