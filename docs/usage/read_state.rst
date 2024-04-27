Read State
==========

..  literalinclude:: read_state_example.py
    :language: python

The output will be something like:

..  code-block:: text

    ADSReadStateResponse(
        result=<ADSErrorCode.ERR_NOERROR: 0>,
        ads_state=<ADSState.ADSSTATE_RUN: 5>,
        device_state=0
    )
