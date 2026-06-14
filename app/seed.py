"""Bootstrap teams and targets from YAML into the database."""

from __future__ import annotations

import argparse
from pathlib import Path

from app.config.loaders import load_targets, load_teams
from app.unit_of_work import unit_of_work


def seed_all(
    *,
    teams_path: Path,
    keys_path: Path,
    services_path: Path,
) -> None:
    teams = load_teams(teams_path, keys_path)
    targets = load_targets(services_path)

    with unit_of_work() as uow:
        for team in teams:
            uow.teams.upsert(team)
        for target in targets:
            uow.targets.upsert(target)


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
