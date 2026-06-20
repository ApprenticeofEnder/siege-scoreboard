from datetime import datetime

from pydantic import BaseModel, NonNegativeInt, PositiveInt


class Tick(BaseModel):
    id: PositiveInt | None = None

    tick_no: NonNegativeInt
    timestamp: datetime

    def __lt__(self, other: "Tick"):
        return self.tick_no < other.tick_no

    def __le__(self, other: "Tick"):
        return self.tick_no <= other.tick_no

    def __gt__(self, other: "Tick"):
        return self.tick_no > other.tick_no

    def __ge__(self, other: "Tick"):
        return self.tick_no >= other.tick_no
