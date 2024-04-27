from ..ads_symbol import ADSSymbol
from ..types import BOOL


def test_ads_symbol() -> None:
    symbol = ADSSymbol("GVL.boolVar", BOOL)
    assert symbol.name == "GVL.boolVar"
    assert symbol.plc_t is BOOL
