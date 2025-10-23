from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, TypeVar, Generic, Type
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class BaseApiClient(ABC, Generic[T]):
    @abstractmethod
    def fetch_data(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[T]] = None,
    ) -> T | Dict[str, Any]:
        """
        Fetches and optionally validates data using a Pydantic model.
        If response_model is provided, returns validated Pydantic instance.
        Otherwise, returns raw dict.
        """
        pass