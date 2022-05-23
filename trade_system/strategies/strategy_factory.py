from trade_system.strategies.change_and_volume_strategy import ChangeAndVolumeStrategy
from trade_system.strategies.base_strategy import IStrategy

__all__ = ("StrategyFactory")


# Фабрика для создания стратегии (1 стратегия - 1 эмитент)
# Процедура добавления новых вариантов стратегий:
# Создание класса стратагия, наследника от IStrategy
# Выбор ему имени для конфигурации и расширение этой фабрики
# Указание имени в конфигурации поле "name" в разделе стратегии
class StrategyFactory:
    @staticmethod
    def new_factory(strategy_name: str, *args, **kwargs) -> IStrategy:
        match strategy_name:
            case "ChangeAndVolumeStrategy":
                return ChangeAndVolumeStrategy(*args, **kwargs)
            case _:
                return None
