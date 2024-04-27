import struct
from dataclasses import dataclass
from typing import Tuple

from typing_extensions import Self

from ..constants.ads_state import ADSState
from ..constants.return_code import ADSErrorCode

# ADS Read State network packet
# https://infosys.beckhoff.com/content/1033/tc3_grundlagen/115878923.html


@dataclass()
class ADSReadStateResponse:
    result: ADSErrorCode
    ads_state: ADSState
    device_state: int

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        s = struct.Struct("< I H H")

        items: Tuple[int, int, int] = s.unpack(data)
        result, ads_state, device_state = items

        return cls(
            result=ADSErrorCode(result),
            ads_state=ADSState(ads_state),
            device_state=device_state,
        )
