from enum import Flag

# AMS Header struct
# https://infosys.beckhoff.com/content/1033/tc3_grundlagen/115847307.html


class StateFlag(Flag):
    AMSCMDSF_RESPONSE = 0x1
    AMSCMDSF_ADSCMD = 0x4
