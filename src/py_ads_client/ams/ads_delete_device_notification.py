import struct
from dataclasses import dataclass
from typing import Tuple

from typing_extensions import Self

from ..constants.return_code import ADSErrorCode

# ADS Delete Device Notification network packet
# https://infosys.beckhoff.com/content/1033/tc3_ads_intro/115881995.html


@dataclass()
class ADSDeleteDeviceNotificationRequest:
    handle: int
    """Handle of notification. The handle is created by the ADS command Add Device Notification."""

    def to_bytes(self) -> bytes:
        return self.handle.to_bytes(length=4, byteorder="little", signed=False)


@dataclass()
class ADSDeleteDeviceNotificationResponse:
    result: ADSErrorCode
    """ADS error number."""

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        s = struct.Struct("< I")
        items: Tuple[int] = s.unpack(data[: s.size])
        result = items[0]
        return cls(result=ADSErrorCode(result))
