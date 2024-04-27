import struct
from abc import ABC, abstractmethod
from datetime import date, datetime, time, timedelta, timezone
from typing import List, Tuple

from .constants.encoding import TWINCAT_STRING_ENCODING, TWINCAT_WSTRING_ENCODING


class PLCData(ABC):

    @property
    @abstractmethod
    def bytes_length(self) -> int: ...


class _PLCBoolType(PLCData):
    def __init__(self) -> None:
        format = "?"
        self.__format = format
        self.__bytes_length = struct.calcsize(format)

    @property
    def bytes_length(self) -> int:
        return self.__bytes_length


class _PLCIntType(PLCData):
    def __init__(self, *, format: str) -> None:
        self.__format = format
        self.__bytes_length = struct.calcsize(format)

    @property
    def bytes_length(self) -> int:
        return self.__bytes_length

    @property
    def is_signed(self) -> bool:
        return self.__format.lower() == self.__format


class _PLCTimeDeltaType(PLCData):
    def __init__(self, *, format: str) -> None:
        self.__format = format
        self.__bytes_length = struct.calcsize(format)

    @property
    def bytes_length(self) -> int:
        return self.__bytes_length

    def decode(self, raw_data: bytes) -> timedelta:
        """Decode time data.

        The precision of the `timedelta` is us, but the PLC only supports ns,
        so ns part will be discarded during decoding.
        """
        if len(raw_data) == 4:
            ms = int.from_bytes(raw_data, byteorder="little", signed=False)
            return timedelta(milliseconds=ms)
        elif len(raw_data) == 8:
            ns = int.from_bytes(raw_data, byteorder="little", signed=False)
            return timedelta(microseconds=ns // 1000)
        else:
            raise ValueError("Invalid time format")

    def encode(self, value: timedelta) -> bytes:
        if self.bytes_length == 4:
            ms = value // timedelta(milliseconds=1)
            return ms.to_bytes(length=4, byteorder="little", signed=False)
        elif self.bytes_length == 8:
            ns = (value // timedelta(microseconds=1)) * 1000
            return ns.to_bytes(length=8, byteorder="little", signed=False)
        else:
            raise ValueError("Invalid time format")


class _PLCDateType(PLCData):
    """TWINCAT DATE data type.

    https://infosys.beckhoff.com/content/1033/tc3_plc_intro/2529415819.html
    """

    def __init__(self, *, format: str) -> None:
        self.__format = format
        self.__bytes_length = struct.calcsize(format)

    @property
    def bytes_length(self) -> int:
        return self.__bytes_length

    def decode(self, raw_data: bytes) -> date:
        if len(raw_data) == 4:
            timestamp = int.from_bytes(raw_data, byteorder="little", signed=False)
            dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            return dt.date()
        else:
            raise ValueError("Invalid date format")

    def encode(self, value: date) -> bytes:
        if self.bytes_length == 4:
            dt = datetime(year=value.year, month=value.month, day=value.day, tzinfo=timezone.utc)
            timestamp = int(dt.timestamp())
            return timestamp.to_bytes(length=4, byteorder="little", signed=False)
        else:
            raise ValueError("Invalid date format")


class _PLCDateAndTimeType(PLCData):
    """TWINCAT DATE_AND_TIME data type.

    https://infosys.beckhoff.com/content/1033/tc3_plc_intro/2529415819.html
    """

    def __init__(self, *, format: str) -> None:
        self.__format = format
        self.__bytes_length = struct.calcsize(format)

    @property
    def bytes_length(self) -> int:
        return self.__bytes_length

    def decode(self, raw_data: bytes) -> datetime:
        if len(raw_data) == 4:
            timestamp = int.from_bytes(raw_data, byteorder="little", signed=False)
            return datetime.fromtimestamp(timestamp, tz=timezone.utc)
        else:
            raise ValueError("Invalid datetime format")

    def encode(self, value: datetime) -> bytes:
        if self.bytes_length == 4:
            timestamp = int(value.timestamp())
            return timestamp.to_bytes(length=4, byteorder="little", signed=False)
        else:
            raise ValueError("Invalid datetime format")


class _PLCTimeOfDayType(PLCData):
    def __init__(self, *, format: str) -> None:
        self.__format = format
        self.__bytes_length = struct.calcsize(format)

    @property
    def bytes_length(self) -> int:
        return self.__bytes_length

    def decode(self, raw_data: bytes) -> time:
        if len(raw_data) == 4:
            ms = int.from_bytes(raw_data, byteorder="little", signed=False)
            hour = ms // 3600000
            minute = (ms % 3600000) // 60000
            second = (ms % 60000) // 1000
            millisecond = ms % 1000
            return time(hour=hour, minute=minute, second=second, microsecond=millisecond * 1000)
        else:
            raise ValueError("Invalid time of day format")

    def encode(self, value: time) -> bytes:
        if self.bytes_length == 4:
            ms = value.hour * 3600000 + value.minute * 60000 + value.second * 1000 + value.microsecond // 1000
            return ms.to_bytes(length=4, byteorder="little", signed=False)
        else:
            raise ValueError("Invalid time of day format")


class _PLCFloatType(PLCData):
    def __init__(self, *, format: str) -> None:
        self.__format = format
        self.__bytes_length = struct.calcsize(format)

    @property
    def bytes_length(self) -> int:
        return self.__bytes_length

    def decode(self, raw_data: bytes) -> float:
        return struct.unpack(self.__format, raw_data)[0]  # type: ignore

    def encode(self, value: float) -> bytes:
        return struct.pack(self.__format, value)


class STRING(PLCData):
    """TWINCAT STRING data type.

    If no size is specified, TwinCAT assumes 80 characters by default.

    The storage space required for a STRING variable is always 1 byte per character + 1 additional byte,
    e.g. 81 bytes for a "STRING(80)" declaration.

    https://infosys.beckhoff.com/content/1033/tc3_plc_intro/2529410443.html
    """

    def __init__(self, length: int = 80) -> None:
        self.__length = length

    @property
    def bytes_length(self) -> int:
        return self.__length + 1

    def decode(self, raw_data: bytes) -> str:
        null_index = raw_data.find(0)
        if null_index != -1:
            raw_data = raw_data[:null_index]
        return raw_data.decode(TWINCAT_STRING_ENCODING)

    def encode(self, text: str) -> bytes:
        return text.encode(TWINCAT_STRING_ENCODING).ljust(self.bytes_length, b"\x00")


class WSTRING(PLCData):
    """TWINCAT WSTRING data type.

    With WSTRING, a length of 10 means that the length of the WSTRING can occupy a maximum of 10 WORDs.

    The data type requires 1 WORD per character and 1 WORD extra memory space.
    The data type WSTRING is terminated with 0.

    https://infosys.beckhoff.com/content/1033/tc3_plc_intro/2529437323.html
    """

    def __init__(self, length: int) -> None:
        self.__length = length

    @property
    def bytes_length(self) -> int:
        return (self.__length + 1) * 2

    def decode(self, raw_data: bytes) -> str:
        null_index = -1
        for i in range(0, len(raw_data), 2):
            if raw_data[i] == 0 and raw_data[i + 1] == 0:
                null_index = i
                break
        if null_index != -1:
            raw_data = raw_data[:null_index]
        return raw_data.decode(TWINCAT_WSTRING_ENCODING)

    def encode(self, text: str) -> bytes:
        return text.encode(TWINCAT_WSTRING_ENCODING).ljust(self.bytes_length, b"\x00")


class ARRAY(PLCData):
    def __init__(self, item_type: PLCData, count: int) -> None:
        self.__item_type = item_type
        self.__count = count

    @property
    def bytes_length(self) -> int:
        return self.__count * self.__item_type.bytes_length

    @property
    def item_type(self) -> PLCData:
        return self.__item_type

    @property
    def length(self) -> int:
        return self.__count


class STRUCT(PLCData):
    def __init__(self, fields: List[Tuple[str, PLCData]]) -> None:
        self.__fields = fields

    @property
    def bytes_length(self) -> int:
        return sum(field.bytes_length for _, field in self.__fields)

    @property
    def fields(self) -> List[Tuple[str, PLCData]]:
        return self.__fields


BOOL = _PLCBoolType()

BYTE = _PLCIntType(format="B")
WORD = _PLCIntType(format="H")
DWORD = _PLCIntType(format="I")
LWORD = _PLCIntType(format="Q")
SINT = _PLCIntType(format="b")
USINT = _PLCIntType(format="B")
INT = _PLCIntType(format="h")
UINT = _PLCIntType(format="H")
DINT = _PLCIntType(format="i")
UDINT = _PLCIntType(format="I")
LINT = _PLCIntType(format="q")
ULINT = _PLCIntType(format="Q")

TIME = _PLCTimeDeltaType(format="I")
LTIME = _PLCTimeDeltaType(format="Q")
DATE = _PLCDateType(format="I")
DATE_AND_TIME = _PLCDateAndTimeType(format="I")
TIME_OF_DAY = _PLCTimeOfDayType(format="I")

REAL = _PLCFloatType(format="f")
LREAL = _PLCFloatType(format="d")
