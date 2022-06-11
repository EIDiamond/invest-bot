import logging

from tinkoff.invest import CandleInterval

from history_tests.strategy_tester import StrategyTester
from history_tests.test_results import TestResults
from invest_api.services.client_service import ClientService
from trade_system.strategies.base_strategy import IStrategy

__all__ = ("HistoryTestsManager")

logger = logging.getLogger(__name__)


class HistoryTestsManager:
    """
    The manager for testing strategy on historical candles
    """

    def __init__(self, client_service: ClientService) -> None:
        self.__client_service = client_service

    def start(
            self,
            strategy: IStrategy,
            from_days: int = 7
    ) -> None:
        """
        Main entry point to start testing
        """
        logger.info(f"Start strategy tests: {strategy}")

        # Download candles for tests
        try:
            candles = self.__client_service.download_historic_candle(
                strategy.settings.figi,
                from_days,
                CandleInterval.CANDLE_INTERVAL_1_MIN
            )
        except Exception as ex:
            logger.error(f"Download candles for tests exception: {repr(ex)}")
            return

        test_results = StrategyTester(strategy).test(candles)

        # Show all results to log file
        self.__log_test_results(test_results)

        logger.info("End strategy tests")

    @staticmethod
    def __log_test_results(test_results: TestResults) -> None:
        """
        Just print results to log file
        """
        logger.info("Test Results:")

        logger.info(f"Signals found: {len(test_results.signals_statuses)}")
        logger.info(f"Proposed Signals: {len(test_results.get_proposed_signals())}")
        logger.info(f"Active Signals: {len(test_results.get_active_signals())}")
        logger.info(f"Take Profit: {len(test_results.get_take_profit_signals())}")
        logger.info(f"Stop Loss: {len(test_results.get_stop_loss_signals())}")
        logger.info(f"Canceled: {len(test_results.get_canceled_signals())}")
