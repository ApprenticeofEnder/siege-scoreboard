from datetime import datetime, timedelta
from pathlib import Path

from pydantic import BaseModel, computed_field


class ServerConfig(BaseModel):
    start_time: datetime
    duration: int
    prep_minutes: int
    tick_length: int
    server: str
    site_folder: Path
    score_cap: int
    negative_score_cap: int
    successful_benign_points: int
    failed_benign_points: int
    successful_malicious_points: int
    failed_malicious_points: int
    down_points: int

    @computed_field
    @property
    def end_time(self) -> datetime:
        return self.start_time + timedelta(minutes=self.duration)

    @computed_field
    @property
    def total_ticks(self) -> int:
        return (self.duration * 60) // self.tick_length

    def tick2time(self, tick: int) -> datetime:
        return self.start_time + timedelta(seconds=tick * self.tick_length)
