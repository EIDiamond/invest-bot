import enum
import logging
from dataclasses import dataclass, field
from decimal import Decimal

__all__ = ("Signal", "SignalType", "SignalStatus", "SignalStatusResult")

logger = logging.getLogger(__name__)


@enum.unique
class SignalType(enum.IntEnum):
    LONG = 0
    SHORT = 1


@dataclass(frozen=True, eq=False, repr=True)
class Signal:
    figi: str = ""
    signal_type: SignalType = 0
    take_profit_level: Decimal = field(default_factory=Decimal)
    stop_loss_level: Decimal = field(default_factory=Decimal)


@enum.unique
class SignalStatusResult(enum.IntEnum):
    PROPOSED = 0
    ACTIVE = 1
    PROFIT = 2
    LOSS = 3
    CANCELED = 4


class SignalStatus:
    def __init__(self, signal: Signal) -> None:
        self.__signal = signal
        self.__result = SignalStatusResult.PROPOSED

    @property
    def signal(self) -> Signal:
        return self.__signal

    def order_activated(self) -> None:
        self.__result = SignalStatusResult.ACTIVE

    def stop_loss_executed(self) -> None:
        self.__result = SignalStatusResult.LOSS

    def take_profit_executed(self) -> None:
        self.__result = SignalStatusResult.PROFIT

    def cancel_executed(self) -> None:
        self.__result = SignalStatusResult.CANCELED

    def is_proposed(self) -> bool:
        return self.__result == SignalStatusResult.PROPOSED

    def is_active(self) -> bool:
        return self.__result == SignalStatusResult.ACTIVE

    def is_take_profit(self) -> bool:
        return self.__result == SignalStatusResult.PROFIT

    def is_stop_loss(self) -> bool:
        return self.__result == SignalStatusResult.LOSS

    def is_canceled(self) -> bool:
        return self.__result == SignalStatusResult.CANCELED

