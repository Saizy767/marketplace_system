from typing import List
from pydantic import BaseModel


class StatItem(BaseModel):
    atbs: int
    avg_pos: float
    clicks: int
    cpc: float
    cpm: float
    ctr: float
    norm_query: str
    orders: int
    shks: int
    views: int


class AdvertStat(BaseModel):
    advert_id: int
    nm_id: int
    stats: List[StatItem]


class StatsResponse(BaseModel):
    stats: List[AdvertStat]