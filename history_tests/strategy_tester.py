import logging

from tinkoff.invest import HistoricCandle
from tinkoff.invest.utils import quotation_to_decimal

from trade_system.strategies.base_strategy import IStrategy
from history_tests.test_results import TestResults

__all__ = ("StrategyTester")

logger = logging.getLogger(__name__)


class StrategyTester:
    def __init__(self, strategy: IStrategy) -> None:
        self.__strategy = strategy

    def test(self,
             candles: list[HistoricCandle],
             portion: int = 1
             ) -> TestResults:
        logger.info(f"Start test: {self.__strategy}, portion {portion}, candles count: {len(candles)}")

        test_result = TestResults()
        test_candles_pack = []

        for candle in candles:
            # проверка сигналов на отработку take или stop
            for signal_status in test_result.get_proposed_signals():
                high = quotation_to_decimal(candle.high)
                low = quotation_to_decimal(candle.low)

                # логика проверки - если диапазон high и low подходит под уровень stop или take, то они отрабатывают
                # Мы не знаем как цена шла в свече, поэтому по худшему сценарию первым проверяем на стоп
                if low <= signal_status.signal.stop_loss_level <= high:
                    signal_status.stop_loss_executed()

                    logger.info("Test STOP LOSS executed")
                    logger.info(f"CANDLE: {candle}")
                    logger.info(f"Signal: {signal_status.signal}")

                elif low <= signal_status.signal.take_profit_level <= high:
                    signal_status.take_profit_executed()

                    logger.info("Test TAKE PROFIT executed")
                    logger.info(f"CANDLE: {candle}")
                    logger.info(f"Signal: {signal_status.signal}")

            # стратегии могут принимать пачку свечей для анализа. По умолчанию в пачке - 1 свеча на анализ
            test_candles_pack.append(candle)

            # набрав пачку отдаем их на анализ
            if len(test_candles_pack) >= portion:
                signal = self.__strategy.analyze_candles(test_candles_pack)
                test_candles_pack = []

                if signal:
                    logger.info(f"New Signal: {signal}")

                    if test_result.get_proposed_signals():
                        logger.info("Signal skipped. Old still alive")
                    else:
                        test_result.add_signal(signal)

        logger.info(f"Tests completed")

        return test_result
