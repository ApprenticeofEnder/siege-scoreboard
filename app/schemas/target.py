from pydantic import BaseModel, Field


class TargetDTO(BaseModel):
    id: int
    name: str
    folder: str
    file: str
    attacker_class: str
    address: str
    description: str
    vulns: int
    req_per_tick: int
    schedule: dict[int, list[int]] = Field(default_factory=dict)
