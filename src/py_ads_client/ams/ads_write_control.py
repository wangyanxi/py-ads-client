import struct
from dataclasses import dataclass

from typing_extensions import Self

from ..constants.ads_state import ADSState
from ..constants.return_code import ADSErrorCode

# ADS Write Control network packet
# https://infosys.beckhoff.com/content/1033/tc3_ads_intro/115879947.html

# In addition to changing the ADS status and the device status,
# it is also possible to send data to the ADS server in order to transfer further information.
# In the current ADS devices (PLC, NC, ...) this data has no further effect.
# https://infosys.beckhoff.com/content/1033/tc3_adsdll2/117542667.html


@dataclass()
class ADSWriteControlRequest:
    ads_state: ADSState
    device_state: int
    data: bytes

    def to_bytes(self) -> bytes:
        length = len(self.data)
        format = f"< H H I {length}s"
        return struct.pack(format, self.ads_state.value, self.device_state, length, self.data)


@dataclass()
class ADSWriteControlResponse:
    result: ADSErrorCode

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        assert len(data) == 4
        code = int.from_bytes(bytes=data, byteorder="little", signed=False)

        return cls(result=ADSErrorCode(code))
