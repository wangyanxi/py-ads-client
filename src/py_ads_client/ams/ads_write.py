import struct
from dataclasses import dataclass
from typing import Tuple

from typing_extensions import Self

from ..constants.index_group import IndexGroup
from ..constants.return_code import ADSErrorCode

# AMS Write network packet
# https://infosys.beckhoff.com/content/1033/tc3_grundlagen/115877899.html


@dataclass()
class ADSWriteRequest:
    index_group: IndexGroup
    """Index Group, in which the data should be written."""
    index_offset: int
    """Index Offset, in which the data should be written."""
    data: bytes
    """Data which are written in the ADS device."""

    def to_bytes(self) -> bytes:
        write_length = len(self.data)
        format = f"< I I I {write_length}s"
        return struct.pack(
            format,
            self.index_group.value,
            self.index_offset,
            write_length,
            self.data,
        )

    @classmethod
    def write_value_by_handle_request(cls, handle: int, data: bytes) -> Self:
        return cls(
            index_group=IndexGroup.SYMVAL_BYHANDLE,
            index_offset=handle,
            data=data,
        )

    @classmethod
    def release_handle(cls, handle: int) -> Self:
        return cls(
            index_group=IndexGroup.RELEASE_SYMHANDLE,
            index_offset=0,
            data=int.to_bytes(handle, 4, byteorder="little", signed=False),
        )


@dataclass()
class ADSWriteResponse:
    result: ADSErrorCode
    """ADS error number."""

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        s = struct.Struct("< I")
        items: Tuple[int] = s.unpack(data)
        result = items[0]
        return cls(result=ADSErrorCode(result))
