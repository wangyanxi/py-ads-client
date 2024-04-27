from ...constants.ads_state import ADSState
from ...constants.return_code import ADSErrorCode
from ..ads_write_control import ADSWriteControlRequest, ADSWriteControlResponse


def test_ads_write_control_request() -> None:
    raw_data = bytes.fromhex("06 00 01 00 00 00 00 00")

    request = ADSWriteControlRequest(ads_state=ADSState.ADSSTATE_STOP, device_state=1, data=b"")

    assert request.to_bytes() == raw_data


def test_ads_write_control_response() -> None:
    raw_data = bytes.fromhex("00 00 00 00")

    response = ADSWriteControlResponse.from_bytes(raw_data)

    assert response.result == ADSErrorCode.ERR_NOERROR
