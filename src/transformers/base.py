from abc import ABC, abstractmethod
from typing import Any, List, Dict

class BaseTransformer(ABC):
    @abstractmethod
    def transform(self, data: Any, **context) -> List[Dict[str, Any]]:
        pass