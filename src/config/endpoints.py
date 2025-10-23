from dataclasses import dataclass
from .settings import settings

@dataclass(frozen=True)
class ApiEndpoints:
    API_BASE_URL: str = settings.api_base_url

    STATISTIC_WORDS: str = f"{API_BASE_URL}/adv/v1/stat/words"


endpoints = ApiEndpoints()