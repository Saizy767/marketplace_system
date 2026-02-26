from typing import List
from pydantic import BaseModel, Field


class StatItem(BaseModel):
    atbs: int = Field(..., description = "Количество добавлений товаров в корзину")
    avg_pos: float = Field(..., description = "Средняя позиция товара на страницах поисковой выдачи")
    clicks: int = Field(..., description = "Количество кликов")
    cpc: float = Field(..., description = "Стоимость одного клика, ₽")
    cpm: float = Field(..., description = "Средняя стоимость за тысячу показов, ₽")
    ctr: float = Field(..., description = "Кликабельность — отношение числа кликов к количеству показов, %")
    norm_query: str = Field(..., description = "Поисковый кластер")
    orders: int = Field(..., description = "Количество заказов")
    shks: int = Field(..., description = "Количество заказанных товаров, шт.")
    views: int = Field(..., description = "Количество просмотров")
    spend: int = Field(..., description = "Затраты на продвижение товаров в конкретном поисковом кластере кампании")


class AdvertStat(BaseModel):
    advert_id: int = Field(..., description = "ID кампании")
    nm_id: int = Field(..., description = "Артикул Wildberries")
    stats: List[StatItem] = Field(..., description = "Статистика кампании")


class StatsResponse(BaseModel):
    stats: List[AdvertStat] = Field(..., description = "Статистика запроса")