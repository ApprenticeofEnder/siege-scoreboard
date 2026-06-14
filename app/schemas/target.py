from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field


class TargetInfo(BaseModel):
    id: int | None = None
    name: str
    folder: str
    file: str
    attacker_class: str
    address: str
    description: str
    req_per_tick: int
    schedule: dict[int, list[int]] = Field(default_factory=dict)


class TargetVulnInfo(BaseModel):
    target_id: int
    request_id: Annotated[int, BeforeValidator(lambda x: x != 0)]

    def is_malicious(self):
        return self.request_id < 0
