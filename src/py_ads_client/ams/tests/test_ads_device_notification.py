from datetime import datetime, timezone

from ..ads_device_notification import ADSDeviceNotificationResponse


def test_device_notification_response() -> None:
    raw_data = bytes.fromhex("1a 00 00 00 01 00 00 00 f0 bc 34 75 33 7b da 01 01 00 00 00 ab 00 00 00 02 00 00 00 02 00")

    request = ADSDeviceNotificationResponse.from_bytes(data=raw_data)
    assert len(request.samples) == 1
    sample = request.samples[0]
    assert sample.timestamp == 0x01DA7B337534BCF0
    assert sample.handle == 0xAB
    assert sample.data == bytes.fromhex("02 00")
    assert sample.update_time == datetime(
        year=2024, month=3, day=21, hour=1, minute=59, second=50, microsecond=79000, tzinfo=timezone.utc
    )
