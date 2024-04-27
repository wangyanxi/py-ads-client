from enum import Enum

# Specification of the ADS system services
# https://infosys.beckhoff.com/content/1033/tc3_ads_intro/117463563.html

# TwinCAT 2 Reserved Index Groups
# https://infosys.beckhoff.com/content/1033/tcplclibsystem/11827998603.html


class IndexGroup(Enum):
    GET_SYMHANDLE_BYNAME = 0xF003
    """A handle (code word) is assigned to the name contained in the write data and is returned to the caller as a result."""
    SYMVAL_BYHANDLE = 0xF005
    """Reads the value of the variable identified by 'symHdl' or assigns a value to the variable."""
    RELEASE_SYMHANDLE = 0xF006
    """The code (handle) contained in the write data for an interrogated, named PLC variable is released."""
