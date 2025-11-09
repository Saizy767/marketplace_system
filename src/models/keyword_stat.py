from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    Date, 
    Index,
    Time)
from src.models.base import Base
from sqlalchemy.dialects.postgresql import JSONB 


class KeywordStat(Base):
    """
    ORM-модель для таблицы keyword_stats в PostgreSQL.
    Хранит агрегированную статистику по ключевым словам для рекламных кампаний.
    """
    __tablename__ = "keyword_stats"
    id = Column(Integer, primary_key=True, autoincrement=True)
    advert_id = Column(String, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    send_time = Column(Time, nullable=False, index=True)
    info_keywords = Column(JSONB, nullable=False)

    __table_args__ = (
        Index("uq_advert_date_keyword",
              "advert_id", "date", "send_time",
              unique=True),
    )