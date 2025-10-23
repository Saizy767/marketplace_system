from pydantic import BaseModel
from typing import List

class KeywordStatistic(BaseModel):
    clicks: int
    keyword: str
    sum: float 
    views: int

class KeywordInsert(BaseModel):
    date: str
    stats: List[KeywordStatistic]

class KeywordListResponse(BaseModel):
    keywords: List[KeywordInsert]