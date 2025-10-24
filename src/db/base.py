from abc import ABC, abstractmethod
from sqlalchemy.engine import Engine

class BaseEngineManager(ABC):

    @abstractmethod
    def get_engine(self) -> Engine:
        pass