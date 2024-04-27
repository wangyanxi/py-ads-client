from typing import Generic, TypeVar

from .types import PLCData

T = TypeVar("T", bound=PLCData, covariant=True)


class ADSSymbol(Generic[T]):
    def __init__(self, name: str, plc_t: T) -> None:
        self.__name = name
        self.__plc_t = plc_t

    @property
    def name(self) -> str:
        return self.__name

    @property
    def plc_t(self) -> T:
        return self.__plc_t
