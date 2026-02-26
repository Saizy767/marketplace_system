from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Subject(BaseModel):
    id: int = Field(..., description="ID предмета")
    name: str = Field(..., description="Название предмета")


class BidsKopecks(BaseModel):
    recommendations: int = Field(..., description="Ставка в рекомендациях")
    search: int = Field(..., description="Ставка в поиске")


class NmSetting(BaseModel):
    bids_kopecks: BidsKopecks = Field(..., description="Ставки, копейки")
    nm_id: int = Field(..., description="Артикул WB")
    subject: Subject = Field(..., description="Предмет")


class Placements(BaseModel):
    recommendations: bool = Field(..., description="Размещение в рекомендациях")
    search: bool = Field(..., description="Размещение в поиске")


class Settings(BaseModel):
    name: str = Field(..., description="Название кампании")
    payment_type: str = Field(..., description="Тип оплаты за показы или за клики")
    placements: Placements = Field(..., description="Места размещения")


class Timestamps(BaseModel):
    created: datetime = Field(..., description="Время создания кампании")
    deleted: datetime = Field(..., description="Время последнего изменения кампании")
    started: Optional[datetime] = Field(None, description="Время последнего запуска кампании")
    updated: datetime = Field(..., description="Время удаления кампании. Если кампания не удалена, время указывается в будущем")


class Advert(BaseModel):
    bid_type: str = Field(..., description="Тип ставки")
    id: int = Field(..., description="ID кампании")
    nm_settings: List[NmSetting] = Field(..., description="Настройки товаров")
    settings: Settings = Field(..., description="Настройки кампании")
    status: int = Field(..., description="Статус кампании")
    timestamps: Timestamps = Field(..., description="Временные отметки")


class ActiveAdvertsResponse(BaseModel):
    adverts: List[Advert] = Field(..., description="Кампании")


class AdvertNmMapping(BaseModel):
    advert_id: int = Field(..., description="ID Кампании")
    nm_id: int = Field(..., description="ID товара")