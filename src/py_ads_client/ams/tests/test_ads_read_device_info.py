from ...constants.return_code import ADSErrorCode
from ..ads_read_device_info import ADSReadDeviceInfoResponse


def test_ads_read_device_info_response() -> None:
    raw_data = bytes.fromhex("00 00 00 00 03 01 a8 07 50 6c 63 33 30 20 41 70 70 00 00 00 00 00 00 00")

    response = ADSReadDeviceInfoResponse.from_bytes(raw_data)

    assert response.result == ADSErrorCode.ERR_NOERROR
    assert response.major_version == 3
    assert response.minor_version == 1
    assert response.build_version == 1960
    assert response.device_name == "Plc30 App"
