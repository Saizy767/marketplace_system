from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseLoader(ABC):
    """
    Абстрактный базовый класс для загрузчиков данных в СУБД.
    Реализации могут использовать ORM, raw SQL или bulk-операции.
    """
    @abstractmethod
    def load(self, records: List[Dict[str, Any]], **context) -> int:
        pass