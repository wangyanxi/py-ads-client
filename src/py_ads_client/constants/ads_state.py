from enum import Enum

# PLC Constants
# https://infosys.beckhoff.com/content/1033/tcplclibsystem/11827998603.html

# C++ ADSSTATE Enum
# https://infosys.beckhoff.com/content/1033/tc3_adsdll2/117556747.html


class ADSState(Enum):
    ADSSTATE_INVALID = 0
    ADSSTATE_IDLE = 1
    ADSSTATE_RESET = 2
    ADSSTATE_INIT = 3
    ADSSTATE_START = 4
    ADSSTATE_RUN = 5
    ADSSTATE_STOP = 6
    ADSSTATE_SAVECFG = 7
    ADSSTATE_LOADCFG = 8
    ADSSTATE_POWERFAILURE = 9
    ADSSTATE_POWERGOOD = 10
    ADSSTATE_ERROR = 11
    ADSSTATE_SHUTDOWN = 12
    ADSSTATE_SUSPEND = 13
    ADSSTATE_RESUME = 14
    ADSSTATE_CONFIG = 15
    """system is in config mode."""
    ADSSTATE_RECONFIG = 16
    """system should restart in config mode."""
