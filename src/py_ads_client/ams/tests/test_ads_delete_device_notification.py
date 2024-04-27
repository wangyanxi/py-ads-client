from ...constants.return_code import ADSErrorCode
from ..ads_delete_device_notification import ADSDeleteDeviceNotificationRequest, ADSDeleteDeviceNotificationResponse


def test_delete_device_notification_request() -> None:
    raw_data = bytes.fromhex("ab 00 00 00")

    request = ADSDeleteDeviceNotificationRequest(handle=0xAB)

    assert request.to_bytes() == raw_data


def test_delete_device_notification_response() -> None:
    raw_data = bytes.fromhex("00 00 00 00")

    response = ADSDeleteDeviceNotificationResponse.from_bytes(raw_data)
    assert response.result == ADSErrorCode.ERR_NOERROR
