from ...constants.index_group import IndexGroup
from ...constants.return_code import ADSErrorCode
from ...constants.transmission_mode import TransmissionMode
from ..ads_add_device_notification import ADSAddDeviceNotificationRequest, ADSAddDeviceNotificationResponse


def test_add_device_notification_request() -> None:
    raw_data = bytes.fromhex("05 f0 00 00 0e 00 80 4b 02 00 00 00 04 00 00 00 01 00 00 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00")

    request = ADSAddDeviceNotificationRequest(
        index_group=IndexGroup.SYMVAL_BYHANDLE,
        index_offset=0x4B80000E,
        length=2,
        transmission_mode=TransmissionMode.ADSTRANS_SERVERONCHA,
        max_delay_ms=1,
        cycle_time_ms=1,
    )

    assert request.to_bytes() == raw_data


def test_add_device_notification_response() -> None:
    raw_data = bytes.fromhex("00 00 00 00 ab 00 00 00")

    response = ADSAddDeviceNotificationResponse.from_bytes(raw_data)

    assert response.result == ADSErrorCode.ERR_NOERROR
    assert response.handle == 0x000000AB
