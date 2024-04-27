Read / Write string value
=========================

TwinCAT supports two types of string variables: ``STRING`` and ``WSTRING``.

Both types are fixed length string (the default length of ``STRING`` is 80).

..  list-table:: Data type conversion
    :align: left
    :header-rows: 1

    * - TwinCAT type
      - Python type
      - Comment
    * - STRING
      - str
      - cp1252 encoding
    * - WSTRING
      - str
      - utf-16 encoding

..  literalinclude:: access_string_variable_example.py
    :language: python
