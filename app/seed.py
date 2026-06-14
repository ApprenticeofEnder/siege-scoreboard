"""Bootstrap teams and targets from YAML into the database."""

from __future__ import annotations

import argparse
from pathlib import Path

import yaml
from pydantic import BaseModel, Field
from sqlmodel import Session, delete

from app.db import engine
from app.models.schedule import TargetScheduleEntry
from app.models.target import Target
from app.models.team import Team


class TeamSeedEntry(BaseModel):
    name: str
    email: str | None = None


class ServiceSeedEntry(BaseModel):
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


def _parse_team_entries(path: Path) -> list[TeamSeedEntry]:
    data = _load_yaml(path)
    raw_teams = data.get("teams", data) if isinstance(data, dict) else data
    return [TeamSeedEntry.model_validate(entry) for entry in raw_teams]


def _parse_keys(path: Path) -> list[str]:
    data = _load_yaml(path)
    if isinstance(data, dict) and "keys" in data:
        keys = data["keys"]
    else:
        keys = data

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


def _parse_service_entries(path: Path) -> list[ServiceSeedEntry]:
    data = _load_yaml(path)
    raw_services = data.get("services", data) if isinstance(data, dict) else data
    entries: list[ServiceSeedEntry] = []
    for entry in raw_services:
        schedule = {
            int(tick): request_ids for tick, request_ids in entry["schedule"].items()
        }
        entries.append(
            ServiceSeedEntry.model_validate({**entry, "schedule": schedule})
        )
    return entries


def seed_teams(session: Session, teams_path: Path, keys_path: Path) -> None:
    team_entries = _parse_team_entries(teams_path)
    keys = _parse_keys(keys_path)

    if len(keys) < len(team_entries):
        msg = (
            f"keys file has {len(keys)} entries but teams file has "
            f"{len(team_entries)} entries"
        )
        raise ValueError(msg)

    for team_id, entry in enumerate(team_entries):
        session.merge(
            Team(
                id=team_id,
                name=entry.name,
                email=entry.email,
                bot_signing_key_pem=keys[team_id],
            )
        )
    session.commit()


def seed_targets(session: Session, services_path: Path) -> None:
    service_entries = _parse_service_entries(services_path)

    for target_id, entry in enumerate(service_entries):
        session.merge(
            Target(
                id=target_id,
                name=entry.name,
                folder=entry.folder,
                file=entry.file,
                attacker_class=entry.cls,
                address=entry.address,
                description=entry.description,
                vulns=entry.vulns,
                req_per_tick=entry.req_per_tick,
            )
        )
        session.commit()

        session.exec(
            delete(TargetScheduleEntry).where(
                TargetScheduleEntry.target_id == target_id
            )
        )
        for tick, request_ids in entry.schedule.items():
            for request_id in request_ids:
                session.add(
                    TargetScheduleEntry(
                        target_id=target_id,
                        tick=tick,
                        request_id=request_id,
                    )
                )
        session.commit()


def seed_all(
    *,
    teams_path: Path,
    keys_path: Path,
    services_path: Path,
) -> None:
    with Session(engine) as session:
        seed_teams(session, teams_path, keys_path)
        seed_targets(session, services_path)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Seed teams and targets from YAML into the database."
    )
    parser.add_argument(
        "--teams",
        type=Path,
        default=Path("example/teams.yaml"),
        help="Path to teams.yaml",
    )
    parser.add_argument(
        "--keys",
        type=Path,
        default=Path("example/keys.yaml"),
        help="Path to keys.yaml",
    )
    parser.add_argument(
        "--services",
        type=Path,
        default=Path("example/services.yaml"),
        help="Path to services.yaml",
    )
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    seed_all(
        teams_path=args.teams,
        keys_path=args.keys,
        services_path=args.services,
    )
    print("Seed complete.")


if __name__ == "__main__":
    main()
