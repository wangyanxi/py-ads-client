import struct

from ...constants.return_code import ADSErrorCode
from ..ads_write import ADSWriteRequest, ADSWriteResponse


def test_ads_write_request() -> None:
    raw_data = bytes.fromhex("05 f0 00 00 0e 00 80 4b 02 00 00 00 02 00")

    data = struct.pack("< H", 0x2)
    request = ADSWriteRequest.write_value_by_handle_request(handle=0x4B80000E, data=data)

    assert request.to_bytes() == raw_data


def test_release_handle_request() -> None:
    raw_data = bytes.fromhex("06 f0 00 00 00 00 00 00 04 00 00 00 03 00 00 5f")

    request = ADSWriteRequest.release_handle(handle=0x5F000003)
    assert request.to_bytes() == raw_data


def test_ads_write_response() -> None:
    raw_data = bytes.fromhex("00 00 00 00")

    response = ADSWriteResponse.from_bytes(raw_data)

    assert response.result == ADSErrorCode.ERR_NOERROR
