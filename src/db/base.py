from abc import ABC, abstractmethod
from sqlalchemy.engine import Engine

class BaseEngineManager(ABC):
    """
    Абстрактный базовый класс для управления подключениями к СУБД через SQLAlchemy Engine.
    """
    @abstractmethod
    def get_engine(self) -> Engine:
        """
        Доработки:
        1) Возможно стоит добавить __enter__ / __exit__ или метод close().
        """
        pass