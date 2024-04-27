import struct
from dataclasses import dataclass
from typing import Tuple

from typing_extensions import Self

from ..constants.encoding import TWINCAT_STRING_ENCODING
from ..constants.return_code import ADSErrorCode

# AMS Read network packet
# https://infosys.beckhoff.com/content/1033/tc3_grundlagen/115875851.html


@dataclass()
class ADSReadDeviceInfoResponse:
    result: ADSErrorCode
    major_version: int
    minor_version: int
    build_version: int
    device_name: str

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        s = struct.Struct("< I B B H 16s")

        items: Tuple[int, int, int, int, bytes] = s.unpack(data)
        result, major, minor, build, name = items

        null_index = name.find(0)
        if null_index != -1:
            name = name[:null_index]

        return cls(
            result=ADSErrorCode(result),
            major_version=major,
            minor_version=minor,
            build_version=build,
            device_name=name.decode(TWINCAT_STRING_ENCODING),
        )

    def to_bytes(self) -> bytes:
        format = "< I B B H 16s"
        return struct.pack(
            format,
            self.result.value,
            self.major_version,
            self.minor_version,
            self.build_version,
            self.device_name.encode(TWINCAT_STRING_ENCODING),
        )
