from datetime import date, datetime, time, timedelta, timezone

import pytest

from ...types import DATE, DATE_AND_TIME, LTIME, TIME, TIME_OF_DAY
from ..decode_ams_payload import decode_ams_payload
from ..encode_ams_payload import encode_ams_payload


@pytest.mark.parametrize(
    "raw_data,td",
    [
        (bytes.fromhex("00 00 00 00"), timedelta(seconds=0)),
        (bytes.fromhex("ff 5b 26 05"), timedelta(hours=23, minutes=59, seconds=59, milliseconds=999)),
        (bytes.fromhex("74 4e b0 05"), timedelta(days=1, hours=2, minutes=30, seconds=40, milliseconds=500)),
        (bytes.fromhex("ff ff ff ff"), timedelta(days=49, hours=17, minutes=2, seconds=47, milliseconds=295)),
    ],
)
def test_plc_time(raw_data: bytes, td: timedelta) -> None:
    assert decode_ams_payload(raw_data=raw_data, plc_t=TIME) == td
    assert encode_ams_payload(data=td, plc_t=TIME) == raw_data


@pytest.mark.parametrize(
    "raw_data,td",
    [
        (bytes.fromhex("00 00 00 00 00 00 00 00"), timedelta(seconds=0)),
        (
            bytes.fromhex("c0 ac af aa 41 ba 1e 00"),
            timedelta(days=100, hours=2, minutes=30, seconds=40, milliseconds=500, microseconds=600),
        ),
        (
            bytes.fromhex("98 fd ff ff ff ff ff ff"),
            timedelta(days=213503, hours=23, minutes=34, seconds=33, milliseconds=709, microseconds=551),
        ),
    ],
)
def test_plc_ltime(raw_data: bytes, td: timedelta) -> None:
    assert decode_ams_payload(raw_data=raw_data, plc_t=LTIME) == td
    assert encode_ams_payload(data=td, plc_t=LTIME) == raw_data


@pytest.mark.parametrize(
    "raw_data,td",
    [
        (bytes.fromhex("00 00 00 00"), date(year=1970, month=1, day=1)),
        (bytes.fromhex("80 a8 3c 5e"), date(year=2020, month=2, day=7)),
        (bytes.fromhex("00 fa 3d 5e"), date(year=2020, month=2, day=8)),
        (
            bytes.fromhex("00 a5 ff ff"),
            date(year=2106, month=2, day=7),
        ),
    ],
)
def test_plc_date(raw_data: bytes, td: datetime) -> None:
    assert decode_ams_payload(raw_data=raw_data, plc_t=DATE) == td
    assert encode_ams_payload(data=td, plc_t=DATE) == raw_data


@pytest.mark.parametrize(
    "raw_data,td",
    [
        (bytes.fromhex("00 00 00 00"), datetime(year=1970, month=1, day=1, tzinfo=timezone.utc)),
        (
            bytes.fromhex("25 5e 3d 5e"),
            datetime(year=2020, month=2, day=7, hour=12, minute=55, second=1, tzinfo=timezone.utc),
        ),
        (
            bytes.fromhex("ff ff ff ff"),
            datetime(year=2106, month=2, day=7, hour=6, minute=28, second=15, tzinfo=timezone.utc),
        ),
    ],
)
def test_plc_date_and_time(raw_data: bytes, td: datetime) -> None:
    assert decode_ams_payload(raw_data=raw_data, plc_t=DATE_AND_TIME) == td
    assert encode_ams_payload(data=td, plc_t=DATE_AND_TIME) == raw_data


@pytest.mark.parametrize(
    "raw_data,td",
    [
        (bytes.fromhex("00 00 00 00"), time(second=0)),
        (bytes.fromhex("f7 fe 95 02"), time(hour=12, minute=3, second=4, microsecond=567000)),
        (bytes.fromhex("ff 5b 26 05"), time(hour=23, minute=59, second=59, microsecond=999000)),
    ],
)
def test_plc_time_of_day(raw_data: bytes, td: time) -> None:
    assert decode_ams_payload(raw_data=raw_data, plc_t=TIME_OF_DAY) == td
    assert encode_ams_payload(data=td, plc_t=TIME_OF_DAY) == raw_data
