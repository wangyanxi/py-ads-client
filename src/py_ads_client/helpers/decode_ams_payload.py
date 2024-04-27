from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Union, overload

from ..types import (
    ARRAY,
    STRING,
    STRUCT,
    WSTRING,
    _PLCBoolType,
    _PLCDateAndTimeType,
    _PLCDateType,
    _PLCFloatType,
    _PLCIntType,
    _PLCTimeDeltaType,
    _PLCTimeOfDayType,
)


@overload
def decode_ams_payload(*, raw_data: bytes, plc_t: _PLCBoolType) -> bool: ...


@overload
def decode_ams_payload(*, raw_data: bytes, plc_t: _PLCIntType) -> int: ...


@overload
def decode_ams_payload(*, raw_data: bytes, plc_t: _PLCFloatType) -> float: ...


@overload
def decode_ams_payload(*, raw_data: bytes, plc_t: _PLCTimeDeltaType) -> timedelta: ...


@overload
def decode_ams_payload(*, raw_data: bytes, plc_t: _PLCDateType) -> date: ...


@overload
def decode_ams_payload(*, raw_data: bytes, plc_t: _PLCDateAndTimeType) -> datetime: ...


@overload
def decode_ams_payload(*, raw_data: bytes, plc_t: _PLCTimeOfDayType) -> time: ...


@overload
def decode_ams_payload(*, raw_data: bytes, plc_t: Union[STRING, WSTRING]) -> str: ...


@overload
def decode_ams_payload(*, raw_data: bytes, plc_t: ARRAY) -> List[Any]: ...


@overload
def decode_ams_payload(*, raw_data: bytes, plc_t: STRUCT) -> Dict[str, Any]: ...


def decode_ams_payload(*, raw_data: bytes, plc_t: Any) -> Any:

    if isinstance(plc_t, _PLCBoolType):
        return bool(raw_data[0])
    elif isinstance(plc_t, _PLCIntType):
        return int.from_bytes(raw_data, byteorder="little", signed=plc_t.is_signed)
    elif isinstance(
        plc_t, (_PLCFloatType, _PLCTimeDeltaType, _PLCDateType, _PLCDateAndTimeType, _PLCTimeOfDayType, STRING, WSTRING)
    ):
        return plc_t.decode(raw_data=raw_data)
    elif isinstance(plc_t, STRUCT):
        data: Dict[str, Any] = {}
        offset = 0
        for name, item_t in plc_t.fields:
            item_bytes_length = item_t.bytes_length
            item_raw_data = raw_data[offset : offset + item_bytes_length]
            offset += item_bytes_length
            data[name] = decode_ams_payload(raw_data=item_raw_data, plc_t=item_t)  # type: ignore
        return data
    elif isinstance(plc_t, ARRAY):
        assert len(raw_data) == plc_t.length * plc_t.item_type.bytes_length
        item_bytes_length = plc_t.item_type.bytes_length
        arr: List[Any] = []
        for i in range(plc_t.length):
            item_raw_data = raw_data[i * item_bytes_length : (i + 1) * item_bytes_length]
            arr.append(decode_ams_payload(raw_data=item_raw_data, plc_t=plc_t.item_type))  # type: ignore
        return arr
    else:
        raise TypeError(f"Unsupported type: {type(plc_t).__name__}")
