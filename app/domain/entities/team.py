from pydantic import BaseModel, PositiveInt


class Team(BaseModel):
    id: PositiveInt | None = None
    name: str
    email: str | None = None
    bot_signing_key_pem: str
