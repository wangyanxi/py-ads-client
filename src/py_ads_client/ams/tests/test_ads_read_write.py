from ...constants.return_code import ADSErrorCode
from ..ads_read_write import ADSReadWriteRequest, ADSReadWriteResponse


def test_ams_read_write_request() -> None:
    raw_data = bytes.fromhex("03 f0 00 00 00 00 00 00 04 00 00 00 0b 00 00 00 47 56 4c 2e 73 74 61 74 75 73 00")

    request = ADSReadWriteRequest.get_handle_by_name(name="GVL.status")

    assert request.to_bytes() == raw_data


def test_ams_read_write_response() -> None:
    raw_data = bytes.fromhex("00 00 00 00 04 00 00 00 0e 00 80 4b")

    response = ADSReadWriteResponse.from_bytes(raw_data)

    assert response.result == ADSErrorCode.ERR_NOERROR
    assert response.data == bytes.fromhex("0e00804b")
    assert response.get_handle_by_name_result == 0x4B80000E
