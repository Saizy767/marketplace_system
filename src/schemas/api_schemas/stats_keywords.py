from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class StatRecord(BaseModel):
    end: datetime
    keyword: str
    campaignName: str
    begin: datetime
    views: int
    advertId: int
    clicks: int
    ctr: float
    cpc: float
    duration: int
    sum: float
    frq: float

class WordsSection(BaseModel):
    phrase: List[str]
    strong: List[str]
    excluded: List[str]
    pluse: List[str]
    keywords: List[dict]

class StatResponse(BaseModel):
    stat: List[StatRecord]
    words: Optional[WordsSection] = None
    fixed: Optional[bool] = None