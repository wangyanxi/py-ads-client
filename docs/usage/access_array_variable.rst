Read / Write array variable
===========================

.. 	code-block:: text

	int1dArrVar : ARRAY[0..4] OF INT;

..  literalinclude:: access_1d_array_example.py
    :language: python

Mutiple level array data types are supportted.

.. 	code-block:: text

	int2dArrVar : ARRAY[0..4] OF ARRAY[0..1] OF INT;
	str2dArrVar : ARRAY[0..4] OF ARRAY[0..1] OF STRING(10);

..  literalinclude:: access_2d_array_example.py
    :language: python

Complex array data types are supportted, such as struct array, string array, etc.

.. code-block:: text

    {attribute 'pack_mode' := '1'}
    TYPE SensorInfo:
    STRUCT
        name: STRING(30);
        value: REAL;
        updateTime: DT;
    END_STRUCT
    END_TYPE

    {attribute 'qualified_only'}
    VAR_GLOBAL
        sensorInfoArrVar: ARRAY[0..2] OF SensorInfo;
    END_VAR

..  literalinclude:: access_struct_array_example.py
    :language: python
