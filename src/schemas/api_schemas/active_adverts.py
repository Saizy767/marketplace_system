from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class Subject(BaseModel):
    id: int
    name: str


class Bids(BaseModel):
    recommendations: int
    search: int


class NmSetting(BaseModel):
    bids: Bids
    nm_id: int
    subject: Subject


class Placements(BaseModel):
    recommendations: bool
    search: bool


class Settings(BaseModel):
    name: str
    payment_type: str
    placements: Placements


class Timestamps(BaseModel):
    created: datetime
    deleted: datetime
    started: Optional[datetime] = None
    updated: datetime


class Advert(BaseModel):
    bid_type: str
    id: int
    nm_settings: List[NmSetting]
    settings: Settings
    status: int
    timestamps: Timestamps


class ActiveAdvertsResponse(BaseModel):
    adverts: List[Advert]