from datetime import date, datetime, time, timedelta, timezone

from ...types import (
    ARRAY,
    BOOL,
    BYTE,
    DATE,
    DATE_AND_TIME,
    DINT,
    DWORD,
    INT,
    LINT,
    LREAL,
    LTIME,
    LWORD,
    REAL,
    SINT,
    STRING,
    STRUCT,
    TIME,
    TIME_OF_DAY,
    UDINT,
    UINT,
    ULINT,
    USINT,
    WORD,
    WSTRING,
)
from ..decode_ams_payload import decode_ams_payload
from ..encode_ams_payload import encode_ams_payload


def test_dict_basic_types() -> None:

    raw_data = bytes.fromhex(
        " ".join(
            [
                "01 a1 b2 a1 d4 c3 b2 a1 b8 a7 f6 e5 d4 c3 b2 a1 85 a1 c7 cf b2 a1 2e fd 69 b6 d4 c3 b2 a1 eb 7e 16 82 0b ef dd ee b8 a7 f6 e5 d4 c3 b2 a1 00 00 c8 42 dd 24 06 81 95 42 8f 40",
                "68 65 6c 6c 6f 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00",
                "60 4f 7d 59 68 00 65 00 6c 00 6c 00 6f 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00",
            ]
        )
    )

    decoded = {
        "boolVar": True,
        "byteVar": 0xA1,
        "wordVar": 0xA1B2,
        "dwordVar": 0xA1B2C3D4,
        "lwordVar": 0xA1B2C3D4E5F6A7B8,
        "sintVar": -123,
        "usintVar": 0xA1,
        "intVar": -12345,
        "uintVar": 0xA1B2,
        "dintVar": -1234567890,
        "udintVar": 0xA1B2C3D4,
        "lintVar": -1234567890123456789,
        "ulintVar": 0xA1B2C3D4E5F6A7B8,
        "realVar": 100.0,
        "lrealVar": 1000.323,
        "stringVar": "hello",
        "wstringVar": "你好hello",
    }

    MyStruct = STRUCT(
        fields=[
            ("boolVar", BOOL),
            ("byteVar", BYTE),
            ("wordVar", WORD),
            ("dwordVar", DWORD),
            ("lwordVar", LWORD),
            ("sintVar", SINT),
            ("usintVar", USINT),
            ("intVar", INT),
            ("uintVar", UINT),
            ("dintVar", DINT),
            ("udintVar", UDINT),
            ("lintVar", LINT),
            ("ulintVar", ULINT),
            ("realVar", REAL),
            ("lrealVar", LREAL),
            ("stringVar", STRING(30)),
            ("wstringVar", WSTRING(30)),
        ]
    )

    assert decode_ams_payload(raw_data=raw_data, plc_t=MyStruct) == decoded
    assert encode_ams_payload(data=decoded, plc_t=MyStruct) == raw_data


def test_date_time_dict() -> None:
    raw_data = bytes.fromhex("74 4e b0 05 c0 ac af aa 41 ba 1e 00 80 a8 3c 5e 25 5e 3d 5e f7 fe 95 02")

    decoded = {
        "timeVar": timedelta(days=1, hours=2, minutes=30, seconds=40, milliseconds=500),
        "ltimeVar": timedelta(days=100, hours=2, minutes=30, seconds=40, milliseconds=500, microseconds=600),
        "dateVar": date(year=2020, month=2, day=7),
        "dateAndTimeVar": datetime(year=2020, month=2, day=7, hour=12, minute=55, second=1, tzinfo=timezone.utc),
        "timeOfDayVar": time(hour=12, minute=3, second=4, microsecond=567000),
    }

    MyStruct = STRUCT(
        fields=[
            ("timeVar", TIME),
            ("ltimeVar", LTIME),
            ("dateVar", DATE),
            ("dateAndTimeVar", DATE_AND_TIME),
            ("timeOfDayVar", TIME_OF_DAY),
        ]
    )

    assert decode_ams_payload(raw_data=raw_data, plc_t=MyStruct) == decoded
    assert encode_ams_payload(data=decoded, plc_t=MyStruct) == raw_data


def test_struct_array() -> None:
    raw_data = bytes.fromhex(
        "01 00 69 64 31 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 02 00 69 64 32 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 03 00 69 64 33 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"
    )
    decoded = [
        {"id": 1, "name": "id1"},
        {"id": 2, "name": "id2"},
        {"id": 3, "name": "id3"},
    ]

    TestInfo = STRUCT(fields=[("id", UINT), ("name", STRING(20))])

    assert decode_ams_payload(raw_data=raw_data, plc_t=ARRAY(TestInfo, 3)) == decoded
    assert encode_ams_payload(data=decoded, plc_t=ARRAY(TestInfo, 3)) == raw_data


def test_dict_array() -> None:
    raw_data = bytes.fromhex(
        " ".join(
            [
                "00 00 0a 00 14 00 1e 00 28 00 32 00 3c 00 46 00 50 00 5a 00",
                "0a 00 0b 00 14 00 15 00 1e 00 1f 00 28 00 29 00 32 00 33 00",
                "30 2c 30 00 00 00 00 00 00 00 00 30 2c 31 00 00 00 00 00 00 00 00 31 2c 30 00 00 00 00 00 00 00 00 31 2c 31 00 00 00 00 00 00 00 00 32 2c 30 00 00 00 00 00 00 00 00 32 2c 31 00 00 00 00 00 00 00 00 33 2c 30 00 00 00 00 00 00 00 00 33 2c 31 00 00 00 00 00 00 00 00 34 2c 30 00 00 00 00 00 00 00 00 34 2c 31 00 00 00 00 00 00 00 00",
                "01 00 69 64 31 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00",
                "02 00 69 64 32 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00",
                "03 00 69 64 33 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00",
                "05 00 69 64 35 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00",
            ]
        )
    )

    decoded = {
        "intArrVar": [0, 10, 20, 30, 40, 50, 60, 70, 80, 90],
        "int2dArrVar": [[10, 11], [20, 21], [30, 31], [40, 41], [50, 51]],
        "str2dArrVar": [["0,0", "0,1"], ["1,0", "1,1"], ["2,0", "2,1"], ["3,0", "3,1"], ["4,0", "4,1"]],
        "structArrVar": [{"id": 1, "name": "id1"}, {"id": 2, "name": "id2"}, {"id": 3, "name": "id3"}],
        "structVar": {"id": 5, "name": "id5"},
    }

    TestInfo = STRUCT(fields=[("id", UINT), ("name", STRING(20))])

    MyStruct = STRUCT(
        fields=[
            ("intArrVar", ARRAY(INT, 10)),
            ("int2dArrVar", ARRAY(ARRAY(UINT, 2), 5)),
            ("str2dArrVar", ARRAY(ARRAY(STRING(10), 2), 5)),
            ("structArrVar", ARRAY(TestInfo, 3)),
            ("structVar", TestInfo),
        ]
    )

    assert decode_ams_payload(raw_data=raw_data, plc_t=MyStruct) == decoded
    assert encode_ams_payload(data=decoded, plc_t=MyStruct) == raw_data
