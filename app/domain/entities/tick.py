from datetime import datetime

from pydantic import BaseModel, NonNegativeInt

from app.domain.exceptions import TickOrderingError
from app.domain.values.database_id import DatabaseId


class Tick(BaseModel):
    id: DatabaseId = None

    tick_num: NonNegativeInt
    timestamp: datetime

    def _ordering_key(self) -> tuple[int, datetime]:
        return (self.tick_num, self.timestamp)

    def _assert_consistent_ordering(self, other: "Tick") -> None:
        if self.tick_num < other.tick_num:
            if self.timestamp >= other.timestamp:
                raise TickOrderingError("The provided ticks have timing errors.")
        elif self.tick_num > other.tick_num:
            if self.timestamp <= other.timestamp:
                raise TickOrderingError("The provided ticks have timing errors.")
        elif self != other:
            raise TickOrderingError("The provided ticks have timing errors.")

    def __lt__(self, other: "Tick"):
        self._assert_consistent_ordering(other)
        return self._ordering_key() < other._ordering_key()

    def __le__(self, other: "Tick"):
        self._assert_consistent_ordering(other)
        return self._ordering_key() <= other._ordering_key()

    def __gt__(self, other: "Tick"):
        self._assert_consistent_ordering(other)
        return self._ordering_key() > other._ordering_key()

    def __ge__(self, other: "Tick"):
        self._assert_consistent_ordering(other)
        return self._ordering_key() >= other._ordering_key()
