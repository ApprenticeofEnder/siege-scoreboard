from pydantic import BaseModel

from app.domain.values.database_id import DatabaseId


class Team(BaseModel):
    id: DatabaseId = None
    name: str
    email: str | None = None
    bot_signing_key_pem: str
