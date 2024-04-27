import pytest

from ...types import ARRAY, BOOL, REAL, STRING, UINT, PLCData
from ..decode_ams_payload import decode_ams_payload
from ..encode_ams_payload import encode_ams_payload


def test_bool_array() -> None:
    raw_data = bytes.fromhex("01 01 00 01 01")
    decoded = [True, True, False, True, True]
    assert decode_ams_payload(raw_data=raw_data, plc_t=ARRAY(BOOL, 5)) == decoded
    assert encode_ams_payload(data=decoded, plc_t=ARRAY(BOOL, 5)) == raw_data


def test_float_array() -> None:
    raw_data = bytes.fromhex("00 00 c8 42 00 00 00 00 00 00 00 00 00 00 00 00 00 00 c8 42")
    decoded = [100, 0, 0, 0, 100.0]
    assert decode_ams_payload(raw_data=raw_data, plc_t=ARRAY(REAL, 5)) == decoded
    assert encode_ams_payload(data=decoded, plc_t=ARRAY(REAL, 5)) == raw_data


def test_int_array() -> None:
    raw_data = bytes.fromhex("00 00 0a 00 14 00 1e 00 28 00 32 00 3c 00 46 00 50 00 5a 00")
    decoded = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
    assert decode_ams_payload(raw_data=raw_data, plc_t=ARRAY(UINT, 10)) == decoded
    assert encode_ams_payload(data=decoded, plc_t=ARRAY(UINT, 10)) == raw_data


def test_2d_int_array() -> None:
    raw_data = bytes.fromhex("0a 00 0b 00 14 00 15 00 1e 00 1f 00 28 00 29 00 32 00 33 00")
    decoded = [[10, 11], [20, 21], [30, 31], [40, 41], [50, 51]]
    assert decode_ams_payload(raw_data=raw_data, plc_t=ARRAY(ARRAY(UINT, 2), 5)) == decoded
    assert encode_ams_payload(data=decoded, plc_t=ARRAY(ARRAY(UINT, 2), 5)) == raw_data


def test_2d_str_array() -> None:
    raw_data = bytes.fromhex(
        "30 2c 30 00 00 00 00 00 00 00 00 30 2c 31 00 00 00 00 00 00 00 00 31 2c 30 00 00 00 00 00 00 00 00 31 2c 31 00 00 00 00 00 00 00 00 32 2c 30 00 00 00 00 00 00 00 00 32 2c 31 00 00 00 00 00 00 00 00 33 2c 30 00 00 00 00 00 00 00 00 33 2c 31 00 00 00 00 00 00 00 00 34 2c 30 00 00 00 00 00 00 00 00 34 2c 31 00 00 00 00 00 00 00 00"
    )
    decoded = [
        ["0,0", "0,1"],
        ["1,0", "1,1"],
        ["2,0", "2,1"],
        ["3,0", "3,1"],
        ["4,0", "4,1"],
    ]
    assert decode_ams_payload(raw_data=raw_data, plc_t=ARRAY(ARRAY(STRING(10), 2), 5)) == decoded
    assert encode_ams_payload(data=decoded, plc_t=ARRAY(ARRAY(STRING(10), 2), 5)) == raw_data


def test_invalid_type() -> None:
    class InvalidType(PLCData):
        def __init__(self) -> None:
            format = "invalid"
            self.__format = format
            self.__bytes_length = 10

        @property
        def bytes_length(self) -> int:
            return self.__bytes_length

    raw_data = bytes.fromhex(
        "30 2c 30 00 00 00 00 00 00 00 00 30 2c 31 00 00 00 00 00 00 00 00 31 2c 30 00 00 00 00 00 00 00 00 31 2c 31 00 00 00 00 00 00 00 00 32 2c 30 00 00 00 00 00 00 00 00 32 2c 31 00 00 00 00 00 00 00 00 33 2c 30 00 00 00 00 00 00 00 00 33 2c 31 00 00 00 00 00 00 00 00 34 2c 30 00 00 00 00 00 00 00 00 34 2c 31 00 00 00 00 00 00 00 00"
    )

    with pytest.raises(TypeError):
        decode_ams_payload(raw_data=raw_data, plc_t=InvalidType())  # type: ignore

    with pytest.raises(TypeError):
        encode_ams_payload(data=12, plc_t=InvalidType())  # type: ignore
