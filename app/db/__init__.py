from collections.abc import Generator

from sqlmodel import Session, SQLModel

from app.engine import engine


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session
