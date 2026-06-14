from sqlmodel import Session

from app.models.team import Team
from app.repositories._helpers import team_to_dto
from app.schemas.team import TeamDTO


class TeamRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def upsert(self, team: TeamDTO) -> TeamDTO:
        row = self._session.merge(
            Team(
                id=team.id,
                name=team.name,
                email=team.email,
                bot_signing_key_pem=team.bot_signing_key_pem,
            )
        )
        self._session.flush()
        return team_to_dto(row)

    def get(self, team_id: int) -> TeamDTO | None:
        row = self._session.get(Team, team_id)
        if row is None:
            return None
        return team_to_dto(row)
