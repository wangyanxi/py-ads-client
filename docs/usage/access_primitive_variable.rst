Read / Write primitive values
=============================

.. list-table:: Data type conversion
   :align: left
   :header-rows: 1

   * - TwinCAT type
     - Python type
     - Comment
   * - BOOL
     - bool
     -
   * - BYTE
     - int
     - 8bit, unsigned
   * - WORD
     - int
     - 16bit, unsigned
   * - DWORD
     - int
     - 32bit, unsigned
   * - LWORD
     - int
     - 64bit, unsigned
   * - SINT
     - int
     - 8bit, signed
   * - INT
     - int
     - 16bit, signed
   * - DINT
     - int
     - 32bit, signed
   * - LINT
     - int
     - 64bit, signed
   * - USINT
     - int
     - 8bit, unsigned
   * - UINT
     - int
     - 16bit, unsigned
   * - UDINT
     - int
     - 32bit, unsigned
   * - ULINT
     - int
     - 64bit, unsigned
   * - REAL
     - float
     - 32bit, float
   * - LREAL
     - float
     - 64bit, float

..  literalinclude:: access_primitive_variable_example.py
    :language: python
