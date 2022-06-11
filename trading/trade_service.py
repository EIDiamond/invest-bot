import datetime
import logging
import time

from blog.blogger import Blogger
from configuration.settings import AccountSettings, TradingSettings
from invest_api.services.accounts_service import AccountService
from invest_api.services.client_service import ClientService
from invest_api.services.instruments_service import InstrumentService
from invest_api.services.market_data_service import MarketDataService
from invest_api.services.operations_service import OperationService
from invest_api.services.orders_service import OrderService
from invest_api.services.market_data_stream_service import MarketDataStreamService
from trade_system.strategies.base_strategy import IStrategy
from trading.trader import Trader

__all__ = ("TradeService")

logger = logging.getLogger(__name__)


class TradeService:
    """
    Represent logic keep trading going
    """
    def __init__(
            self,
            account_service: AccountService,
            client_service: ClientService,
            instrument_service: InstrumentService,
            operation_service: OperationService,
            order_service: OrderService,
            stream_service: MarketDataStreamService,
            market_data_service: MarketDataService,
            blogger: Blogger
    ) -> None:
        self.__account_service = account_service
        self.__client_service = client_service
        self.__instrument_service = instrument_service
        self.__operation_service = operation_service
        self.__order_service = order_service
        self.__stream_service = stream_service
        self.__market_data_service = market_data_service
        self.__blogger = blogger

    def start_trading(
            self,
            account_settings: AccountSettings,
            trading_settings: TradingSettings,
            strategies: list[IStrategy]
    ) -> None:
        try:
            logger.info("Finding account for trading")
            account_id = self.__account_service.trading_account_id(account_settings)

            if not account_id:
                logger.error("Account for trading hasn't been found")
                return None

            logger.info(f"Account id: {account_id}")

        except Exception as ex:
            logger.error(f"Start trading error: {repr(ex)}")
            return None

        self.__working_loop(account_id, trading_settings, strategies, account_settings.min_rub_on_account)

    def __working_loop(
            self,
            account_id: str,
            trading_settings: TradingSettings,
            strategies: list[IStrategy],
            min_rub: int
    ) -> None:
        logger.info("Start every day trading")

        while True:
            logger.info("Check trading schedule on today")

            try:
                is_trading_day, start_time, end_time = \
                    self.__instrument_service.moex_today_trading_schedule()
                # for tests
                # is_trading_day, start_time, end_time = \
                #    True, \
                #    datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) + datetime.timedelta(seconds=10), \
                #    datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) + datetime.timedelta(minutes=12)

                if is_trading_day and datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) <= end_time:
                    logger.info(f"Today is trading day. Trading will start after {start_time}")

                    TradeService.__sleep_to(
                        start_time + datetime.timedelta(seconds=trading_settings.delay_start_after_open)
                    )

                    logger.info(f"Trading day has been started")

                    Trader(
                        client_service=self.__client_service,
                        instrument_service=self.__instrument_service,
                        operation_service=self.__operation_service,
                        order_service=self.__order_service,
                        stream_service=self.__stream_service,
                        market_data_service=self.__market_data_service,
                        blogger=self.__blogger
                    ).trade_day(account_id, trading_settings, strategies, end_time, min_rub)

                    logger.info("Trading day has been completed")
                else:
                    logger.info("Today is not trading day. Sleep on next morning")
            except Exception as ex:
                logger.error(f"Start trading today error: {repr(ex)}")

            logger.info("Sleep to next morning")
            TradeService.__sleep_to_next_morning()

    @staticmethod
    def __sleep_to_next_morning() -> None:
        future = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        next_time = datetime.datetime(year=future.year, month=future.month, day=future.day,
                                      hour=6, minute=0, tzinfo=datetime.timezone.utc)

        TradeService.__sleep_to(next_time)

    @staticmethod
    def __sleep_to(next_time: datetime) -> None:
        now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

        logger.debug(f"Sleep from {now} to {next_time}")
        total_seconds = (next_time - now).total_seconds()

        if total_seconds > 0:
            time.sleep(total_seconds)
