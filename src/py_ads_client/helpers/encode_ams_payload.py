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
def encode_ams_payload(*, data: bool, plc_t: _PLCBoolType) -> bytes: ...


@overload
def encode_ams_payload(*, data: int, plc_t: _PLCIntType) -> bytes: ...


@overload
def encode_ams_payload(*, data: float, plc_t: _PLCFloatType) -> bytes: ...


@overload
def encode_ams_payload(*, data: timedelta, plc_t: _PLCTimeDeltaType) -> bytes: ...


@overload
def encode_ams_payload(*, data: date, plc_t: _PLCDateType) -> bytes: ...


@overload
def encode_ams_payload(*, data: datetime, plc_t: _PLCDateAndTimeType) -> bytes: ...


@overload
def encode_ams_payload(*, data: time, plc_t: _PLCTimeOfDayType) -> bytes: ...


@overload
def encode_ams_payload(*, data: str, plc_t: Union[STRING, WSTRING]) -> bytes: ...


@overload
def encode_ams_payload(*, data: List[Any], plc_t: ARRAY) -> bytes: ...


@overload
def encode_ams_payload(*, data: Dict[str, Any], plc_t: STRUCT) -> bytes: ...


def encode_ams_payload(*, data: Any, plc_t: Any) -> bytes:

    if isinstance(plc_t, _PLCBoolType):
        assert isinstance(data, bool)
        return bytes([data])
    elif isinstance(plc_t, _PLCIntType):
        assert isinstance(data, int)
        return data.to_bytes(length=plc_t.bytes_length, byteorder="little", signed=plc_t.is_signed)
    elif isinstance(plc_t, _PLCFloatType):
        assert isinstance(data, (float, int))
        return plc_t.encode(data)
    elif isinstance(plc_t, _PLCTimeDeltaType):
        assert isinstance(data, timedelta)
        return plc_t.encode(data)
    elif isinstance(plc_t, _PLCDateType):
        assert isinstance(data, date)
        return plc_t.encode(data)
    elif isinstance(plc_t, _PLCDateAndTimeType):
        assert isinstance(data, datetime)
        return plc_t.encode(data)
    elif isinstance(plc_t, _PLCTimeOfDayType):
        assert isinstance(data, time)
        return plc_t.encode(data)
    elif isinstance(plc_t, (STRING, WSTRING)):
        assert isinstance(data, str)
        return plc_t.encode(data)
    elif isinstance(plc_t, STRUCT):
        assert isinstance(data, dict)
        raw_data = b""
        for name, item_t in plc_t.fields:
            item_v = data[name]
            raw_data += encode_ams_payload(data=item_v, plc_t=item_t)  # type: ignore
        return raw_data
    elif isinstance(plc_t, ARRAY):
        assert isinstance(data, list)
        assert len(data) == plc_t.length
        raw_data = b""
        for i in range(len(data)):
            raw_data += encode_ams_payload(data=data[i], plc_t=plc_t.item_type)  # type: ignore
        return raw_data
    else:
        raise TypeError(f"Unsupported type: {type(plc_t).__name__}")
