from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseExtractor(ABC):
    """
    Базовый интерфейс для любого экстрактора данных.
    """

    @abstractmethod
    def extract(self, entity: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Извлекает сырые записи из источника для заданной сущности.
        
        Args:
            entity (str): Название сущности (например, "invoices", "products")
            **kwargs: Дополнительные параметры (фильтры, дата начала и т.д.)
        
        Returns:
            List[Dict[str, Any]]: Список сырых записей в формате JSON-подобных словарей
        """
        pass

    @abstractmethod
    def list_entities(self) -> List[str]:
        """
        Возвращает список поддерживаемых сущностей (опционально, для автоматизации).
        """
        pass