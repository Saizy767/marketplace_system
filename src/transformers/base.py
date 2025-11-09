from abc import ABC, abstractmethod
from typing import Any, List, Dict

class BaseTransformer(ABC):
    """
    Абстрактный базовый класс для трансформеров данных.
    Определяет единый интерфейс: метод `transform` принимает сырые данные
    и контекст выполнения, возвращает список словарей для последующей
    загрузки в СУБД.
    """
    @abstractmethod
    def transform(self, data: Any, **context) -> List[Dict[str, Any]]:
        pass