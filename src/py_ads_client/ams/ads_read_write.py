import struct
from dataclasses import dataclass
from typing import Tuple

from typing_extensions import Self

from ..constants.encoding import TWINCAT_STRING_ENCODING
from ..constants.index_group import IndexGroup
from ..constants.return_code import ADSErrorCode

# ADS Read Write packet
# https://infosys.beckhoff.com/content/1033/tc3_grundlagen/115884043.html


@dataclass()
class ADSReadWriteRequest:
    index_group: IndexGroup
    """Index Group, in which the data should be written."""
    index_offset: int
    """Index Offset, in which the data should be written."""
    read_length: int
    """Length of data in bytes, which should be read."""
    write_data: bytes
    """Data which are written in the ADS device."""

    def to_bytes(self) -> bytes:
        write_length = len(self.write_data)
        format = f"< I I I I {write_length}s"
        return struct.pack(
            format,
            self.index_group.value,
            self.index_offset,
            self.read_length,
            write_length,
            self.write_data,
        )

    @classmethod
    def get_handle_by_name(cls, name: str) -> Self:
        data = name.encode(encoding=TWINCAT_STRING_ENCODING) + b"\x00"
        return cls(
            index_group=IndexGroup.GET_SYMHANDLE_BYNAME,
            index_offset=0,
            read_length=4,
            write_data=data,
        )


@dataclass()
class ADSReadWriteResponse:
    result: ADSErrorCode
    """ADS error number."""
    data: bytes
    """Data which are supplied back."""

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        s = struct.Struct("< I I")
        items: Tuple[int, int] = s.unpack(data[: s.size])
        result, data_length = items
        body = data[s.size :]
        assert len(body) == data_length
        return cls(result=ADSErrorCode(result), data=body)

    @property
    def get_handle_by_name_result(self) -> int:
        item: Tuple[int] = struct.unpack("< I", self.data)
        return item[0]
