from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from app.schemas.target import TargetDTO
from app.schemas.team import TeamDTO


class _TeamYamlEntry(BaseModel):
    name: str
    email: str | None = None


class _ServiceYamlEntry(BaseModel):
    name: str
    folder: str
    file: str
    cls: str
    address: str
    description: str
    vulns: int
    req_per_tick: int
    schedule: dict[int, list[int]] = Field(default_factory=dict)


def _load_yaml(path: Path) -> object:
    with path.open() as handle:
        return yaml.safe_load(handle)


def _parse_team_entries(path: Path) -> list[_TeamYamlEntry]:
    data = _load_yaml(path)
    raw_teams = data.get("teams", data) if isinstance(data, dict) else data
    if not isinstance(raw_teams, list):
        msg = f"Expected team list in {path}"
        raise ValueError(msg)
    return [_TeamYamlEntry.model_validate(entry) for entry in raw_teams]


def _parse_keys(path: Path) -> list[str]:
    data = _load_yaml(path)
    if isinstance(data, dict) and "keys" in data:
        keys = data["keys"]
    else:
        keys = data

    if not isinstance(keys, list):
        msg = f"Expected key list in {path}"
        raise ValueError(msg)

    parsed: list[str] = []
    for entry in keys:
        if isinstance(entry, str):
            parsed.append(entry.strip())
        elif isinstance(entry, dict):
            parsed.append(str(entry["key"]).strip())
        else:
            msg = f"Unsupported key entry format: {entry!r}"
            raise ValueError(msg)
    return parsed


def _parse_service_entries(path: Path) -> list[_ServiceYamlEntry]:
    data = _load_yaml(path)
    raw_services = data.get("services", data) if isinstance(data, dict) else data
    if not isinstance(raw_services, list):
        msg = f"Expected service list in {path}"
        raise ValueError(msg)

    entries: list[_ServiceYamlEntry] = []
    for entry in raw_services:
        if not isinstance(entry, dict):
            msg = f"Expected service mapping in {path}"
            raise ValueError(msg)
        schedule = {
            int(tick): request_ids for tick, request_ids in entry["schedule"].items()
        }
        entries.append(
            _ServiceYamlEntry.model_validate({**entry, "schedule": schedule})
        )
    return entries


def load_teams(teams_path: Path, keys_path: Path) -> list[TeamDTO]:
    team_entries = _parse_team_entries(teams_path)
    keys = _parse_keys(keys_path)

    if len(keys) < len(team_entries):
        msg = (
            f"keys file has {len(keys)} entries but teams file has "
            f"{len(team_entries)} entries"
        )
        raise ValueError(msg)

    return [
        TeamDTO(
            id=team_id,
            name=entry.name,
            email=entry.email,
            bot_signing_key_pem=keys[team_id],
        )
        for team_id, entry in enumerate(team_entries)
    ]


def load_targets(services_path: Path) -> list[TargetDTO]:
    service_entries = _parse_service_entries(services_path)
    return [
        TargetDTO(
            id=target_id,
            name=entry.name,
            folder=entry.folder,
            file=entry.file,
            attacker_class=entry.cls,
            address=entry.address,
            description=entry.description,
            vulns=entry.vulns,
            req_per_tick=entry.req_per_tick,
            schedule=entry.schedule,
        )
        for target_id, entry in enumerate(service_entries)
    ]
