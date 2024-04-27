from ...constants.command_id import ADSCommand
from ...constants.return_code import ADSErrorCode
from ...constants.state_flag import StateFlag
from ..ams_header import AMSHeader


def test_ams_header() -> None:
    raw_data = bytes.fromhex("c0 a8 58 64 01 01 53 03 c0 a8 58 14 01 01 30 75 09 00 04 00 37 00 00 00 00 00 00 00 01 00 00 00")
    header = AMSHeader.from_bytes(raw_data)

    assert header.target_net_id == "192.168.88.100.1.1"
    assert header.target_port == 851
    assert header.source_net_id == "192.168.88.20.1.1"
    assert header.source_port == 30000
    assert header.command_id == ADSCommand.ADSSRVID_READWRITE
    assert header.state_flags == StateFlag.AMSCMDSF_ADSCMD
    assert header.length == 55
    assert header.error_code == ADSErrorCode.ERR_NOERROR
    assert header.invoke_id == 1

    assert header.to_bytes() == raw_data
