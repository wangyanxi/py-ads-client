from datetime import datetime, time, timedelta

import pytest

from ..types import (
    DATE,
    DATE_AND_TIME,
    TIME,
    TIME_OF_DAY,
    _PLCDateAndTimeType,
    _PLCDateType,
    _PLCTimeDeltaType,
    _PLCTimeOfDayType,
)


def test_time_invalid_type() -> None:
    with pytest.raises(ValueError, match="Invalid time format"):
        TIME.decode(bytes.fromhex("00"))

    with pytest.raises(ValueError, match="Invalid time format"):
        td = timedelta(seconds=1)
        INVALID = _PLCTimeDeltaType(format="H")
        INVALID.encode(td)


def test_date_invalid_type() -> None:
    with pytest.raises(ValueError, match="Invalid date format"):
        DATE.decode(bytes.fromhex("00"))

    with pytest.raises(ValueError, match="Invalid date format"):
        d = datetime.now()
        INVALID = _PLCDateType(format="H")
        INVALID.encode(d.date())


def test_date_time_invalid_type() -> None:
    with pytest.raises(ValueError, match="Invalid datetime format"):
        DATE_AND_TIME.decode(bytes.fromhex("00"))

    with pytest.raises(ValueError, match="Invalid datetime format"):
        d = datetime.now()
        INVALID = _PLCDateAndTimeType(format="H")
        INVALID.encode(d)


def test_time_of_day_invalid_type() -> None:
    with pytest.raises(ValueError, match="Invalid time of day format"):
        TIME_OF_DAY.decode(bytes.fromhex("00"))

    with pytest.raises(ValueError, match="Invalid time of day format"):
        t = time(hour=12)
        INVALID = _PLCTimeOfDayType(format="H")
        INVALID.encode(t)
