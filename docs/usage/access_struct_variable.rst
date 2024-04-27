Read / Write struct variable
============================


..  code-block:: text
    :caption: PLC structure definition

    {attribute 'pack_mode' := '1'}
    TYPE SensorInfo:
    STRUCT
        name: STRING(30);
        value: REAL;
        updateTime: DATE_AND_TIME;
    END_STRUCT
    END_TYPE

..  literalinclude:: access_struct_variable_example.py
    :language: python
