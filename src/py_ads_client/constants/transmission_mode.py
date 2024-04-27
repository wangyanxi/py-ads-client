from enum import Enum

# C++ ADSTRANSMODE Enum
# https://infosys.beckhoff.com/content/1033/tc3_adsdll2/117558283.html

# C++ AdsNotificationAttrib struct
# https://infosys.beckhoff.com/content/1033/tc3_adsdll2/117553803.html


class TransmissionMode(Enum):
    ADSTRANS_NOTRANS = 0
    ADSTRANS_CLIENTCYCLE = 1
    ADSTRANS_CLIENT1REQ = 2
    ADSTRANS_SERVERCYCLE = 3
    """The notification's callback function is invoked cyclically."""
    ADSTRANS_SERVERONCHA = 4
    """The notification's callback function is only invoked when the value changes."""
