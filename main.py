import logging
import os
from logging.handlers import RotatingFileHandler

from blog.blogger import Blogger
from configuration.configuration import ProgramConfiguration, WorkingMode
from history_tests.history_manager import HistoryTestsManager
from invest_api.services.accounts_service import AccountService
from invest_api.services.client_service import ClientService
from invest_api.services.instruments_service import InstrumentService
from invest_api.services.market_data_service import MarketDataService
from invest_api.services.operations_service import OperationService
from invest_api.services.orders_service import OrderService
from invest_api.services.market_data_stream_service import MarketDataStreamService
from trade_system.strategies.strategy_factory import StrategyFactory
from trading.trade_service import TradeService

# the configuration file name
CONFIG_FILE = "settings.ini"

if __name__ == "__main__":
    if not os.path.exists("logs/"):
        os.makedirs("logs/")

    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(module)s - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
        handlers=[RotatingFileHandler('logs/robot.log', maxBytes=100000000, backupCount=10, encoding='utf-8')],
        encoding="utf-8"
    )

    logger.info("Program start")

    try:
        config = ProgramConfiguration(CONFIG_FILE)
        logger.info("Configuration has been loaded")
    except Exception as ex:
        logger.critical("Load configuration error: %s", repr(ex))
    else:
        account_service = AccountService(config.tinkoff_token, config.tinkoff_app_name)
        client_service = ClientService(config.tinkoff_token, config.tinkoff_app_name)
        instrument_service = InstrumentService(config.tinkoff_token, config.tinkoff_app_name)
        operation_service = OperationService(config.tinkoff_token, config.tinkoff_app_name)
        order_service = OrderService(config.tinkoff_token, config.tinkoff_app_name)
        stream_service = MarketDataStreamService(config.tinkoff_token, config.tinkoff_app_name)
        market_data_service = MarketDataService(config.tinkoff_token, config.tinkoff_app_name)

        if account_service.verify_token():
            logger.info(f"Working mode is {config.working_mode.name} ({config.working_mode})")

            match config.working_mode:
                case WorkingMode.HISTORICAL_MODE:
                    test_strategy = StrategyFactory.new_factory(
                        config.test_strategy_settings.name,
                        config.test_strategy_settings
                    )

                    HistoryTestsManager(client_service).start(test_strategy)

                case WorkingMode.SANDBOX_MODE:
                    pass

                case WorkingMode.TRADE_MODE:
                    logger.info(f"Blog settings: {config.blog_settings}")
                    blogger = Blogger(config.blog_settings, config.trade_strategy_settings)

                    trade_strategies = [StrategyFactory.new_factory(x.name, x) for x in config.trade_strategy_settings]

                    TradeService(
                        account_service=account_service,
                        client_service=client_service,
                        instrument_service=instrument_service,
                        operation_service=operation_service,
                        order_service=order_service,
                        stream_service=stream_service,
                        market_data_service=market_data_service,
                        blogger=blogger
                    ). start_trading(
                        config.account_settings,
                        config.trading_settings,
                        trade_strategies
                    )

                case _:
                    logger.warning("Working mode is unsupported")
        else:
            logger.critical("Client verification has been failed")

    logger.info("Program end")
