Read Device Info
================

..  literalinclude:: read_device_info_example.py
    :language: python

The output will be something like:

..  code-block:: text

    ADSReadDeviceInfoResponse(
        result=<ADSErrorCode.ERR_NOERROR: 0>,
        major_version=3,
        minor_version=1,
        build_version=1960,
        device_name='Plc30 App'
    )
