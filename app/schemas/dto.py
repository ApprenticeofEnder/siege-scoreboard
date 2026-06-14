from pydantic import BaseModel

from app.schemas.target import AttackRecordInfo, AttackResult


class TickResultDTO(BaseModel):
    team_id: int
    tick: int
    results: dict[int, list[list[int]]]

    def to_attack_records(self) -> list[AttackRecordInfo]:
        result: list[AttackRecordInfo] = []

        for target_id, target_results in self.results.items():
            for request_id, attack_result in target_results:
                attack_record = AttackRecordInfo(
                    target_id=target_id,
                    request_id=request_id,
                    team_id=self.team_id,
                    tick=self.tick,
                    result=AttackResult(attack_result),
                )
                result.append(attack_record)
        return result
