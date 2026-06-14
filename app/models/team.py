# pyright: reportUndefinedVariable=false

from sqlmodel import Field, Relationship, SQLModel


class Team(SQLModel, table=True):
    __tablename__: str = "teams"

    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str | None = None
    bot_signing_key_pem: str

    tick_submissions: list["TickSubmission"] = Relationship(back_populates="team")
