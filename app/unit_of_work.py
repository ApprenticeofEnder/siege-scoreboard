from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass

from sqlmodel import Session

from app.engine import engine
from app.repositories.target import TargetRepository
from app.repositories.team import TeamRepository
from app.repositories.tick import TickSubmissionRepository


@dataclass
class UnitOfWork:
    session: Session
    teams: TeamRepository
    targets: TargetRepository
    ticks: TickSubmissionRepository

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()


@contextmanager
def unit_of_work(session: Session | None = None) -> Generator[UnitOfWork]:
    owns_session = session is None
    active_session = Session(engine) if owns_session else session

    uow = UnitOfWork(
        session=active_session,
        teams=TeamRepository(active_session),
        targets=TargetRepository(active_session),
        ticks=TickSubmissionRepository(active_session),
    )
    try:
        yield uow
        active_session.commit()
    except Exception:
        active_session.rollback()
        raise
    finally:
        if owns_session:
            active_session.close()


def get_unit_of_work() -> Generator[UnitOfWork]:
    with unit_of_work() as uow:
        yield uow
