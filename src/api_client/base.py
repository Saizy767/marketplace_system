from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, TypeVar, Generic, Type
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class BaseApiClient(ABC, Generic[T]):
    """
    Абстрактный базовый класс для клиентов API.
    Обеспечивает единообразный интерфейс для получения и, при необходимости,
    валидации данных из внешних источников с использованием Pydantic.
    """
    @abstractmethod
    def fetch_data(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None,
    ) -> T | Dict[str, Any]:
        pass