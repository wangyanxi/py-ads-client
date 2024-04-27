import struct
from dataclasses import dataclass
from typing import Tuple

from typing_extensions import Self

from ..constants.command_id import ADSCommand
from ..constants.return_code import ADSErrorCode
from ..constants.state_flag import StateFlag

# AMS Header struct
# https://infosys.beckhoff.com/content/1033/tc3_grundlagen/115847307.html


@dataclass()
class AMSHeader:
    target_net_id: str
    target_port: int
    source_net_id: str
    source_port: int
    command_id: ADSCommand
    state_flags: StateFlag
    length: int
    """Size of the data range. The unit is byte."""
    error_code: ADSErrorCode
    """AMS error number."""
    invoke_id: int
    """Free usable 32 bit array. Usually this array serves to send an Id."""

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        s = struct.Struct("< 6s H 6s H H H I I I")
        items: Tuple[bytes, int, bytes, int, int, int, int, int, int] = s.unpack(data)
        (
            target_net_id,
            target_port,
            source_net_id,
            source_port,
            command_id,
            state_flags,
            length,
            error_code,
            invoke_id,
        ) = items
        target_net_id_str = ".".join(str(x) for x in target_net_id)
        source_net_id_str = ".".join(str(x) for x in source_net_id)
        command_id_enum = ADSCommand(command_id)
        state_flags_enum = StateFlag(state_flags)
        error_code_enum = ADSErrorCode(error_code)

        return cls(
            target_net_id=target_net_id_str,
            target_port=target_port,
            source_net_id=source_net_id_str,
            source_port=source_port,
            command_id=command_id_enum,
            state_flags=state_flags_enum,
            length=length,
            error_code=error_code_enum,
            invoke_id=invoke_id,
        )

    def to_bytes(self) -> bytes:
        target_net_id = bytes(int(x) for x in self.target_net_id.split("."))
        source_net_id = bytes(int(x) for x in self.source_net_id.split("."))
        return struct.pack(
            "< 6s H 6s H H H I I I",
            target_net_id,
            self.target_port,
            source_net_id,
            self.source_port,
            self.command_id.value,
            self.state_flags.value,
            self.length,
            self.error_code.value,
            self.invoke_id,
        )
