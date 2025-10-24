from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseLoader(ABC):
    @abstractmethod
    def load(self, records: List[Dict[str, Any]], **context) -> int:
        pass