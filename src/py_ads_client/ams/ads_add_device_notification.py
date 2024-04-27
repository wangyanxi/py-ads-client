import struct
from dataclasses import dataclass
from typing import Tuple

from typing_extensions import Self

from ..constants.index_group import IndexGroup
from ..constants.return_code import ADSErrorCode
from ..constants.transmission_mode import TransmissionMode

# ADS Add Device Notification network packet
# https://infosys.beckhoff.com/content/1033/tc3_ads_intro/115880971.html

# C++ AdsNotificationAttrib struct
# https://infosys.beckhoff.com/content/1033/tc3_adsdll2/117553803.html


@dataclass()
class ADSAddDeviceNotificationRequest:
    index_group: IndexGroup
    index_offset: int
    """Index Offset, in which the data should be written."""
    length: int
    """Length of data in bytes, which should be read."""
    max_delay_ms: int
    """At the latest after this time, the ADS Device Notification is called. The unit is 1ms."""
    cycle_time_ms: int
    """The ADS server checks if the value changes in this time slice. The unit is 1ms."""
    transmission_mode: TransmissionMode = TransmissionMode.ADSTRANS_SERVERONCHA

    def to_bytes(self) -> bytes:
        reserved = bytes(16)
        format = "< I I I I I I 16s"
        return struct.pack(
            format,
            self.index_group.value,
            self.index_offset,
            self.length,
            self.transmission_mode.value,
            self.max_delay_ms,
            self.cycle_time_ms,
            reserved,
        )


@dataclass()
class ADSAddDeviceNotificationResponse:
    result: ADSErrorCode
    """ADS error number."""
    handle: int
    """Data which are supplied back."""

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        s = struct.Struct("< I I")
        items: Tuple[int, int] = s.unpack(data[: s.size])
        result, handle = items
        return cls(result=ADSErrorCode(result), handle=handle)
