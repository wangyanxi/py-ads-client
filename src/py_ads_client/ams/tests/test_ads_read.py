from ...constants.index_group import IndexGroup
from ...constants.return_code import ADSErrorCode
from ..ads_read import ADSReadRequest, ADSReadResponse


def test_ads_read_request() -> None:
    raw_data = bytes.fromhex("05 f0 00 00 03 00 00 5f 05 00 00 00")

    request = ADSReadRequest(index_group=IndexGroup.SYMVAL_BYHANDLE, index_offset=0x5F000003, length=5)

    assert request.to_bytes() == raw_data


def test_ads_write_response() -> None:
    raw_data = bytes.fromhex("00 00 00 00 05 00 00 00 01 01 00 01 01")

    response = ADSReadResponse.from_bytes(raw_data)

    assert response.result == ADSErrorCode.ERR_NOERROR
    assert response.data == bytes.fromhex("01 01 00 01 01")
