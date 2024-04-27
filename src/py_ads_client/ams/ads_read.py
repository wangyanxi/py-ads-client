import struct
from dataclasses import dataclass
from typing import Tuple

from typing_extensions import Self

from ..constants.index_group import IndexGroup
from ..constants.return_code import ADSErrorCode

# AMS Read network packet
# https://infosys.beckhoff.com/content/1033/tc3_grundlagen/115876875.html


@dataclass()
class ADSReadRequest:
    index_group: IndexGroup
    index_offset: int
    length: int
    """Length of the data (in bytes) which should be read."""

    def to_bytes(self) -> bytes:
        format = "< I I I"
        return struct.pack(
            format,
            self.index_group.value,
            self.index_offset,
            self.length,
        )


@dataclass()
class ADSReadResponse:
    result: ADSErrorCode
    data: bytes

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        s = struct.Struct("< I I")
        items: Tuple[int, int] = s.unpack(data[: s.size])
        result, length = items
        assert len(data) == length + s.size
        return cls(result=ADSErrorCode(result), data=data[s.size :])
