PLC method call
===============

PLC method define.

.. 	code-block:: text

    {attribute 'TcRpcEnable'}
    METHOD echo : STRING(130)
    VAR_INPUT
        user: STRING(20);
        message: STRING(100);
    END_VAR

    echo := CONCAT(CONCAT(user, ': '), message);

Python code to call the method.

..  literalinclude:: method_call.py
    :language: python
    :lines: 22-45
