from datetime import datetime

import pytest

from app.domain.entities.tick import Tick
from app.domain.exceptions import TickOrderingError
from tests.domain.conftest import TickFactory


def test_tick_le(create_tick: TickFactory):
    ticks: list[Tick] = [create_tick(tick_num=i) for i in range(2)]

    assert ticks[0] <= ticks[1]


def test_tick_lt(create_tick: TickFactory):
    ticks: list[Tick] = [create_tick(tick_num=i) for i in range(2)]

    assert ticks[0] < ticks[1]


def test_tick_gt(create_tick: TickFactory):
    ticks: list[Tick] = [create_tick(tick_num=i) for i in range(2)]

    assert ticks[1] > ticks[0]


def test_tick_ge(create_tick: TickFactory):
    ticks: list[Tick] = [create_tick(tick_num=i) for i in range(2)]

    assert ticks[1] >= ticks[0]


def test_tick_ordering_rejects_equal_timestamp_with_higher_tick_num(
    create_tick: TickFactory,
):
    timestamp = datetime(2020, 1, 1, 12, 0, 0)
    earlier = create_tick(tick_num=0, timestamp=timestamp)
    later = create_tick(tick_num=1, timestamp=timestamp)

    with pytest.raises(TickOrderingError):
        _ = earlier < later


def test_tick_ordering_rejects_timestamp_regression(create_tick: TickFactory):
    earlier = create_tick(tick_num=0, timestamp=datetime(2020, 1, 1, 12, 0, 1))
    later = create_tick(tick_num=1, timestamp=datetime(2020, 1, 1, 12, 0, 0))

    with pytest.raises(TickOrderingError):
        _ = earlier < later


def test_tick_eq_does_not_raise(create_tick: TickFactory):
    first = create_tick(tick_num=1, timestamp=datetime(2020, 1, 1, 12, 0, 0))
    second = create_tick(tick_num=1, timestamp=datetime(2020, 1, 1, 12, 0, 1))

    assert first != second
