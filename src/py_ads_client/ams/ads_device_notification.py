from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List

from typing_extensions import Self

# C++ AdsNotificationHeader struct
# https://infosys.beckhoff.com/content/1033/tc3_adsdll2/117554827.html


@dataclass()
class AdsNotificationSample:
    handle: int
    timestamp: int
    data: bytes

    @property
    def update_time(self) -> datetime:
        # A file time is a 64-bit value that represents the number of 100-nanosecond intervals that have elapsed
        # since 12:00 A.M. January 1, 1601 Coordinated Universal Time (UTC).
        EPOCH_AS_FILETIME = 116444736000000000  # January 1, 1970 as MS file time
        unix_timestamp_us = (self.timestamp - EPOCH_AS_FILETIME) // 10
        return datetime.fromtimestamp(0, tz=timezone.utc) + timedelta(microseconds=unix_timestamp_us)


@dataclass()
class ADSDeviceNotificationResponse:
    samples: List[AdsNotificationSample]

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        total_size = int.from_bytes(data[:4], byteorder="little", signed=False)
        assert len(data) == total_size + 4
        stamp_count = int.from_bytes(data[4:8], byteorder="little", signed=False)

        offset = 8
        samples: List[AdsNotificationSample] = []
        for _ in range(stamp_count):
            filetime = int.from_bytes(data[offset : offset + 8], byteorder="little", signed=False)
            offset += 8
            sample_count = int.from_bytes(data[offset : offset + 4], byteorder="little", signed=False)
            offset += 4
            for _ in range(sample_count):
                handle = int.from_bytes(bytes=data[offset : offset + 4], byteorder="little", signed=False)
                sample_size = int.from_bytes(bytes=data[offset + 4 : offset + 8], byteorder="little", signed=False)
                sample_data = data[offset + 8 : offset + 8 + sample_size]
                sample = AdsNotificationSample(handle=handle, timestamp=filetime, data=sample_data)
                samples.append(sample)
                offset += 8 + sample_size

        return cls(samples=samples)
