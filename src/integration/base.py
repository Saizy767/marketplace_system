from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseExtractor(ABC):
    """
    Базовый интерфейс для любого экстрактора данных.
    """

    @abstractmethod
    def extract(self, entity: str, **kwargs) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def list_entities(self) -> List[str]:
        pass