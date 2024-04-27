from enum import Enum


class ADSCommand(Enum):
    ADSSRVID_READDEVICEINFO = 0x1
    """Reads the name and the version number of the ADS device."""
    ADSSRVID_READ = 0x2
    """With ADS Read data can be read from an ADS device."""
    ADSSRVID_WRITE = 0x3
    """With ADS Write data can be written to an ADS device."""
    ADSSRVID_READSTATE = 0x4
    """Reads the ADS status and the device status of an ADS device."""
    ADSSRVID_WRITECTRL = 0x5
    """Changes the ADS status and the device status of an ADS device."""
    ADSSRVID_ADDDEVICENOTE = 0x6
    """A notification is created in an ADS device."""
    ADSSRVID_DELDEVICENOTE = 0x7
    """One before defined notification is deleted in an ADS device."""
    ADSSRVID_DEVICENOTE = 0x8
    """Data will carry forward independently from an ADS device to a Client."""
    ADSSRVID_READWRITE = 0x9
    """With ADS ReadWrite data will be written to an ADS device. Additionally, data can be read from the ADS device."""
