import requests
from typing import Dict, Any, Optional, Type, TypeVar, Union
from pydantic import BaseModel, ValidationError
from .base import BaseApiClient
from src.config.settings import Settings


T = TypeVar("T", bound=BaseModel)


class GenericApiClient(BaseApiClient):
    """
    Универсальный клиент для выполнения HTTP GET-запросов к внешнему API.
    """
    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def fetch_data(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None,
    ) -> Union[T, Dict[str, Any], list]:
        """
        Выполняет GET-запрос к указанному URL и возвращает данные.
        
        Параметры:
        - url: полный URL эндпоинта
        - headers: дополнительные HTTP-заголовки (сливаются с Authorization)
        - params: query-параметры
        - response_model: Pydantic-модель для валидации и парсинга JSON
        
        Возвращает:
        - Экземпляр Pydantic-модели T — если response_model указан и валидация успешна.
        - dict или list — если response_model не указан (сырой JSON).
        
        В случае ошибки выбрасывает RuntimeError с понятным сообщением.

        Доработки:
        1) Создать кастомные исключения
        2) При временной ошибке (503) запрос не повторяется
        """
        settings = Settings()
        default_headers = {
            "Authorization": f"{settings.api_key}"
        }

        merged_headers = {**default_headers, **(headers or {})}

        try:
            response = requests.get(
                url=url,
                headers=merged_headers,
                params=params or {},
                timeout=self.timeout
            )
            response.raise_for_status()
            raw_data = response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"HTTP request failed: {e}") from e
        except ValueError as e:
            raise RuntimeError(f"Invalid JSON response: {e}") from e

        if response_model:
            try:
                return response_model.model_validate(raw_data)
            except ValidationError as e:
                raise RuntimeError(f"Response validation failed: {e}") from e

        return raw_data