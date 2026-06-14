from sqlmodel import Session, col, delete, select

from app.models.target import Target, TargetScheduleEntry
from app.repositories._helpers import require_id, target_to_dto
from app.schemas.target import TargetDTO


class TargetRepository:
    _session: Session

    def __init__(self, session: Session) -> None:
        self._session = session

    def upsert(self, target: TargetDTO) -> TargetDTO:
        self._session.merge(
            Target(
                id=target.id,
                name=target.name,
                folder=target.folder,
                file=target.file,
                attacker_class=target.attacker_class,
                address=target.address,
                description=target.description,
                vulns=target.vulns,
                req_per_tick=target.req_per_tick,
            )
        )
        self._session.exec(
            delete(TargetScheduleEntry).where(
                col(TargetScheduleEntry.target_id) == target.id
            )
        )
        for tick, request_ids in target.schedule.items():
            for request_id in request_ids:
                self._session.add(
                    TargetScheduleEntry(
                        target_id=target.id,
                        tick=tick,
                        request_id=request_id,
                    )
                )
        self._session.flush()
        return target

    def get(self, target_id: int) -> TargetDTO | None:
        row = self._session.get(Target, target_id)
        if row is None:
            return None
        schedule_entries = self._session.exec(
            select(TargetScheduleEntry).where(
                col(TargetScheduleEntry.target_id) == target_id
            )
        ).all()
        return target_to_dto(row, list(schedule_entries))

    def list_all(self) -> list[TargetDTO]:
        targets = self._session.exec(select(Target).order_by(col(Target.id))).all()
        if not targets:
            return []

        target_ids = [require_id(target) for target in targets]
        schedule_entries = self._session.exec(
            select(TargetScheduleEntry).where(
                col(TargetScheduleEntry.target_id).in_(target_ids)
            )
        ).all()
        entries_by_target: dict[int, list[TargetScheduleEntry]] = {
            target_id: [] for target_id in target_ids
        }
        for entry in schedule_entries:
            entries_by_target[entry.target_id].append(entry)

        return [
            target_to_dto(target, entries_by_target[require_id(target)])
            for target in targets
        ]
