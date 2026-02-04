import requests
from typing import Dict, Any, Optional, Type, TypeVar, Union
from pydantic import BaseModel, ValidationError
from .base import BaseApiClient
from src.config.settings import Settings
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


T = TypeVar("T", bound=BaseModel)


class GenericApiClient(BaseApiClient):
    """
    Универсальный клиент для выполнения HTTP GET-запросов к внешнему API.
    """
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()

        retry_strategy = Retry(
            total=3,
            backoff_factor=4,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
            connect=3,
            read=3,
            redirect=False,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)


    def fetch_data(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None,
    ) -> Union[T, Dict[str, Any], list]:
        """
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
    

    def post_data(
        self,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None,
    ) -> Union[T, Dict[str, Any], list]:
        """
        Отправка данных через POST запрос
        
        Доработки:
        1) Создать кастомные исключения
        2) При временной ошибке (503) запрос не повторяется
        
        Args:
            url: URL для отправки запроса
            json: Данные для отправки в формате JSON (автоматически сериализуется)
            data: Данные для отправки в формате form-data
            headers: Дополнительные заголовки
            params: Query параметры (в URL)
            response_model: Pydantic модель для валидации ответа
            
        Returns:
            Валидированный объект модели или сырые данные
        """
        settings = Settings()
        default_headers = {
            "Authorization": f"{settings.api_key}"
        }

        merged_headers = {**default_headers, **(headers or {})}

        try:
            response = requests.post(
                url=url,
                headers=merged_headers,
                params=params or {},
                json=json,
                data=data,
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