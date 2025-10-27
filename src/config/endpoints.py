from dataclasses import dataclass
from .settings import Settings

@dataclass(frozen=True)
class ApiEndpoints:
    api_base_url: str
    api_key: str

    @property
    def ACTIVE_ADVERTS(self) -> str:
        return f"{self.api_base_url}/adv/v0/auction/adverts"

    @property
    def STATISTIC_WORDS(self) -> str:
        return f"{self.api_base_url}/adv/v1/stat/words"

def get_endpoints() -> ApiEndpoints:
    settings = Settings()
    return ApiEndpoints(
        api_base_url=settings.api_base_url,
        api_key=settings.api_key,
    )