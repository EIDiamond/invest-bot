from trade_system.signal import SignalStatus, Signal

__all__ = ("TestResults")


class TestResults:
    def __init__(self):
        self.__signals_statuses = []

    @property
    def signals_statuses(self) -> list[SignalStatus]:
        return self.__signals_statuses

    def add_signal(self, signal: Signal) -> None:
        self.__signals_statuses.append(SignalStatus(signal))

    def get_take_profit_signals(self) -> list[SignalStatus]:
        return list(filter(lambda x: x.is_take_profit(), self.__signals_statuses))

    def get_stop_loss_signals(self) -> list[SignalStatus]:
        return list(filter(lambda x: x.is_stop_loss(), self.__signals_statuses))

    def get_proposed_signals(self) -> list[SignalStatus]:
        return list(filter(lambda x: x.is_proposed(), self.__signals_statuses))

    def get_canceled_signals(self) -> list[SignalStatus]:
        return list(filter(lambda x: x.is_canceled(), self.__signals_statuses))

    def get_active_signals(self) -> list[SignalStatus]:
        return list(filter(lambda x: x.is_active(), self.__signals_statuses))
