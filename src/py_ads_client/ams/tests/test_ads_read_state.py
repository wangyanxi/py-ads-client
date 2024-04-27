from ...constants.ads_state import ADSState
from ...constants.return_code import ADSErrorCode
from ..ads_read_state import ADSReadStateResponse


def test_ads_read_device_info_response() -> None:
    raw_data = bytes.fromhex("00 00 00 00 05 00 00 00")

    response = ADSReadStateResponse.from_bytes(raw_data)

    assert response.result == ADSErrorCode.ERR_NOERROR
    assert response.ads_state == ADSState.ADSSTATE_RUN
    assert response.device_state == 0
