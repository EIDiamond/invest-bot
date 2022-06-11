import datetime
import logging
from typing import Generator

from tinkoff.invest import Client, CandleInstrument, SubscriptionInterval, InfoInstrument, TradeInstrument, \
    MarketDataResponse, Candle
from tinkoff.invest.market_data_stream.market_data_stream_manager import MarketDataStreamManager

__all__ = ("MarketDataStreamService")

logger = logging.getLogger(__name__)


class MarketDataStreamService:
    """
    The class encapsulate tinkoff market data stream (gRPC) service api
    """
    def __init__(self, token: str, app_name: str) -> None:
        self.__token = token
        self.__app_name = app_name
        self.__market_data_candles_stream: MarketDataStreamManager = None

    def start_candles_stream(
            self,
            figies: list[str],
            trade_before_time: datetime
    ) -> Generator[Candle, None, None]:
        """
        The method starts gRPC stream and return candles
        """
        logger.debug(f"Starting candles stream")

        self.__stop_candles_stream()

        with Client(self.__token, app_name=self.__app_name) as client:
            self.__market_data_candles_stream: MarketDataStreamManager = client.create_market_data_stream()

            logger.info(f"Subscribe candles: {figies}")
            self.__market_data_candles_stream.candles.subscribe(
                [
                    CandleInstrument(
                        figi=figi,
                        interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE
                    )
                    for figi in figies
                ]
            )

            for market_data in self.__market_data_candles_stream:
                logger.debug(f"market_data: {market_data}")

                # trading will stop at trade_before_time
                if datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) >= trade_before_time:
                    logger.debug(f"Time to stop candle stream")
                    self.__stop_candles_stream()
                    break

                if market_data.candle:
                    yield market_data.candle

        self.__stop_candles_stream()

    def __stop_candles_stream(self) -> None:
        if self.__market_data_candles_stream:
            logger.info(f"Stopping candles stream")
            self.__market_data_candles_stream.stop()
            self.__market_data_candles_stream = None
