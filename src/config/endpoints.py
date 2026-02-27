from dataclasses import dataclass
from .settings import Settings

@dataclass(frozen=True)
class ApiEndpoints:
    """
    Хранит URL-адреса эндпоинтов внешнего API.
    Не содержит секретов — api_key используется только для отладки/логгирования.
    """
    api_base_url: str
    api_statistic_url: str
    api_seller_url: str
    api_key: str

    @property
    def ACTIVE_ADVERTS(self) -> str:
        return f"{self.api_base_url}/api/advert/v2/adverts"

    @property
    def STATISTIC_WORDS(self) -> str:
        return f"{self.api_base_url}/adv/v0/normquery/stats"
    
    @property
    def ORDERS_LIST(self) -> str:
        return f"{self.api_statistic_url}/api/v1/supplier/orders"
    
    @property
    def SALES_FUNNEL(self) -> str:
        return f"{self.api_seller_url}/api/analytics/v3/sales-funnel/products/history"


def get_endpoints() -> ApiEndpoints:
    settings = Settings()
    return ApiEndpoints(
        api_base_url=settings.api_base_url,
        api_statistic_url=settings.api_statistic_url,
        api_seller_url=settings.api_seller_url,
        api_key=settings.api_key,
    )