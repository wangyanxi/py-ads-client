Read / Write time value
=======================

..  list-table:: Data type conversion
    :align: left
    :header-rows: 1

    * - TwinCAT type
      - Python type
      - Comment
    * - TIME
      - timedelta
      - 32bit, in ms
    * - LTIME
      - timedelta
      - 64bit, in ns
    * - DATE
      - date
      - 32bit, in seconds, but only the date part
    * - DATE_AND_TIME
      - datetime
      - 32bit, in seconds, unix timestamp
    * - TIME_OF_DAY
      - time
      - 32bit, in ms

..  warning::

    The precision of ``LTIME`` is nanosecond, and the precision of ``timedelta`` is microsecond, the ns part will be discarded during the conversion of LTIME to timedelta.

    for example: ``LTIME#100d2h30m40s500ms600us700ns`` will be converted to ``timedelta(days=100, hours=2, minutes=30, seconds=40, milliseconds=500, microseconds=600)``.

..  literalinclude:: access_time_variable_example.py
    :language: python
