import logging
from decimal import Decimal

from tinkoff.invest import OrderState

from configuration.settings import BlogSettings, StrategySettings
from invest_api.utils import moneyvalue_to_decimal
from tg_api.telegram_service import TelegramService
from trade_system.signal import SignalType
from trade_system.strategies.base_strategy import IStrategy
from trading.trade_results import TradeOrder

__all__ = ("Blogger")

logger = logging.getLogger(__name__)


class Blogger:
    def __init__(self, blog_settings: BlogSettings, trade_strategies: list[StrategySettings]) -> None:
        self.__blog_status = blog_settings.blog_status
        self.__trade_strategies: dict[str, StrategySettings] = {x.figi : x for x in trade_strategies}

        self.__init_tg(blog_settings.bot_token, blog_settings.chat_id)

    def __init_tg(self, token: str, chat_id: str) -> None:
        try:
            self.__telegram_service = TelegramService(
                token=token,
                chat_id=chat_id
            )
        except Exception as ex:
            logger.error(f"Error init tg service {repr(ex)}")
            # Ошибка инициализации TG отключает блог.
            # Отключенный блог не помеха трейдингу
            self.__blog_status = False

    def __send_text_message(self, text: str) -> None:
        try:
            logger.debug(f"Message to telegram: {text}")

            self.__telegram_service.send_text_message(text)
        except Exception as ex:
            logger.error(f"Error send message to telegram {repr(ex)}")

    def start_trading_message(self,
                              today_trade_strategy: dict[str, IStrategy],
                              rub_before_trade_day: Decimal) -> None:
        if self.__blog_status:
            self.__send_text_message("Приветствую! Начинаем торговлю.")
            self.__send_text_message(f"Размер депо: {rub_before_trade_day:.2f} rub")
            self.__send_text_message("Сегодня следим за следующими акциями:")
            for figi_key, strategy_value in today_trade_strategy.items():
                self.__send_text_message(f"Ticker: {strategy_value.settings.ticker}. "
                                         f"Разрешен шорт: {strategy_value.settings.short_enabled_flag}")

    def finish_trading_message(self) -> None:
        if self.__blog_status:
            self.__send_text_message("Заканчиваем торговлю.")

    def close_position_message(self, trade_order: TradeOrder) -> None:
        if self.__blog_status and trade_order:
            signal_type = Blogger.__signal_type_to_message_test(trade_order.signal.signal_type)
            self.__send_text_message(
                f"Закрываем {signal_type} позицию по {self.__trade_strategies[trade_order.signal.figi].ticker}")

    def open_position_message(self, trade_order: TradeOrder) -> None:
        if self.__blog_status and trade_order:
            signal_type = Blogger.__signal_type_to_message_test(trade_order.signal.signal_type)
            self.__send_text_message(
                f"Открываем {signal_type} позицию по {self.__trade_strategies[trade_order.signal.figi].ticker}. "
                f"Уровень take profit: {trade_order.signal.take_profit_level:.2f}. "
                f"Уровень stop loss: {trade_order.signal.stop_loss_level:.2f}.")

    def trading_depo_summary_message(self,
                                     rub_before_trade_day: Decimal,
                                     current_rub_on_depo: Decimal) -> None:
        if self.__blog_status:
            self.__send_text_message(f"Итоги по размеру депо за торговую сессию. "
                                     f"Было:{rub_before_trade_day:.2f} стало:{current_rub_on_depo:.2f}")

            today_profit = current_rub_on_depo - rub_before_trade_day
            today_percent_profit = (today_profit / rub_before_trade_day) * 100
            self.__send_text_message(f"Прибыль:{today_profit:.2f} rub ({today_percent_profit:.2f} %)")

    def fail_message(self):
        if self.__blog_status:
            self.__send_text_message(f"Во время торговли что-то пошло не так. Пробую закрыть позиции. "
                                     f"Все оставшиеся не закрытые позиции надо закрыть вручную.")

    def summary_message(self):
        if self.__blog_status:
            self.__send_text_message(f"Подводим итоги торговой сессии:")

    def final_message(self):
        if self.__blog_status:
            self.__send_text_message(f"Торговля окончена. До встречи!")

    def summary_open_signal_message(self, trade_order: TradeOrder, open_order_state: OrderState):
        if self.__blog_status:
            signal_type = Blogger.__signal_type_to_message_test(trade_order.signal.signal_type)
            summary_commission = moneyvalue_to_decimal(open_order_state.executed_commission) + \
                                 moneyvalue_to_decimal(open_order_state.service_commission)
            self.__send_text_message(f"Открытый {signal_type} сигнал по {self.__trade_strategies[trade_order.signal.figi].ticker}. "
                                     f"Исполнено лотов: {open_order_state.lots_executed}. "
                                     f"Средняя цена при открытии позиции: "
                                     f"{moneyvalue_to_decimal(open_order_state.average_position_price):.2f}. "
                                     f"Полная стоимость сделки: "
                                     f"{moneyvalue_to_decimal(open_order_state.total_order_amount):.2f}. "
                                     f"Сумма всех комиссий: "
                                     f"{summary_commission:.2f}. "
                                     f"Позицию надо закрыть вручную.")

    def summary_closed_signal_message(self,
                                      trade_order: TradeOrder,
                                      open_order_state: OrderState,
                                      close_order_state: OrderState):
        if self.__blog_status:
            signal_type = Blogger.__signal_type_to_message_test(trade_order.signal.signal_type)
            summary_commission = moneyvalue_to_decimal(open_order_state.executed_commission) + \
                                 moneyvalue_to_decimal(open_order_state.service_commission) + \
                                 moneyvalue_to_decimal(close_order_state.executed_commission) + \
                                 moneyvalue_to_decimal(close_order_state.service_commission)
            self.__send_text_message(f"Отработанный {signal_type} сигнал по {self.__trade_strategies[trade_order.signal.figi].ticker}. "
                                     f"Исполнено лотов: {close_order_state.lots_executed}. "
                                     f"Средняя цена при открытии позиции: "
                                     f"{moneyvalue_to_decimal(open_order_state.average_position_price):.2f}. "
                                     f"Средняя цена при закрытии позиции: "
                                     f"{moneyvalue_to_decimal(close_order_state.average_position_price):.2f}. "
                                     f"Результат сделки: "
                                     f"{moneyvalue_to_decimal(close_order_state.total_order_amount) - moneyvalue_to_decimal(open_order_state.total_order_amount):.2f}. "
                                     f"Сумма всех комиссий: "
                                     f"{summary_commission:.2f}.")

    @staticmethod
    def __signal_type_to_message_test(signal_type: SignalType) -> str:
        return "лонг" if signal_type == SignalType.LONG else "шорт"