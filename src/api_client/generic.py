import requests
from typing import Dict, Any, Optional, Type, TypeVar, Union, get_origin, get_args
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
        # Ensure token has a scheme (Bearer) if not provided by Settings
        api_key = settings.api_key or ""
        if api_key.startswith("Bearer ") or api_key.startswith("Token "):
            auth_value = api_key
        else:
            auth_value = f"Bearer {api_key}"

        default_headers = {
            "Authorization": auth_value
        }

        merged_headers = {**default_headers, **(headers or {})}

        try:
            response = self.session.get(
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
                origin = get_origin(response_model)
                if origin is list:
                    item_type = get_args(response_model)[0]
                    if hasattr(item_type, "model_validate") and isinstance(raw_data, list):
                        return [item_type.model_validate(item) for item in raw_data]
                    return raw_data

                # Handle Pydantic model classes (e.g. OrdersResponse)
                if hasattr(response_model, "model_validate"):
                    if isinstance(raw_data, list) and getattr(response_model, "model_fields", None) and "orders" in response_model.model_fields:
                        raw_data = {"orders": raw_data}

                    return response_model.model_validate(raw_data)

                return raw_data
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
        api_key = settings.api_key or ""
        if api_key.startswith("Bearer ") or api_key.startswith("Token "):
            auth_value = api_key
        else:
            auth_value = f"Bearer {api_key}"

        default_headers = {
            "Authorization": auth_value
        }

        merged_headers = {**default_headers, **(headers or {})}

        try:
            response = self.session.post(
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