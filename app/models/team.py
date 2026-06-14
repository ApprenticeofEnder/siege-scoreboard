from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.schemas import TeamDTO

if TYPE_CHECKING:
    from app.models.tick import TickSubmission


class Team(SQLModel, table=True):
    __tablename__: str = "teams"

    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str | None = None
    bot_signing_key_pem: str

    tick_submissions: list["TickSubmission"] = Relationship(back_populates="team")

    def to_dto(self) -> TeamDTO:
        assert self.id is not None
        return TeamDTO(
            id=self.id,
            name=self.name,
            email=self.email,
            bot_signing_key_pem=self.bot_signing_key_pem,
        )
