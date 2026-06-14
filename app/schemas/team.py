from pydantic import BaseModel


class TeamDTO(BaseModel):
    id: int | None = None
    name: str
    email: str | None = None
    bot_signing_key_pem: str
