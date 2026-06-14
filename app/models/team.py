from app.models.base import BaseDbModelWithId


class Team(BaseDbModelWithId, table=True):
    __tablename__: str = "teams"

    name: str
    email: str | None = None
    bot_signing_key_pem: str
