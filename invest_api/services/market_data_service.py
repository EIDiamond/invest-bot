import logging

from tinkoff.invest import Client, GetTradingStatusResponse, SecurityTradingStatus

from invest_api.invest_error_logging import invest_error_logging

__all__ = ("MarketDataService")

logger = logging.getLogger(__name__)


class MarketDataService:
    def __init__(self, token: str, app_name: str) -> None:
        self.__token = token
        self.__app_name = app_name

    @invest_error_logging
    def __get_trading_status(self, figi: str) -> GetTradingStatusResponse:
        with Client(self.__token, app_name=self.__app_name) as client:
            status = client.market_data.get_trading_status(figi=figi)

            logger.debug(f"Trading Status {figi}: {status}")

            return status

    def is_stock_ready_for_trading(self, figi: str) -> bool:
        # признак доступности акций для торговли:
        # разрешены лимитные заявки
        # разрешены рыночные заявки
        # можно торговать по API
        # статус - обычная торговля
        # робот не торгует в другие статусы, даже если выставление заявок возможно
        # например: дискретный аукцион (не инвестиционная рекомендация :) )

        status = self.__get_trading_status(figi)

        return status.limit_order_available_flag and \
               status.market_order_available_flag and \
               status.api_trade_available_flag and \
               status.trading_status == SecurityTradingStatus.SECURITY_TRADING_STATUS_NORMAL_TRADING
