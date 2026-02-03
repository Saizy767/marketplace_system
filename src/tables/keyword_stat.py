from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    Date, 
    Index,
    Numeric,
    Time)
from src.tables.base import Base


class KeywordStat(Base):
    """
    ORM-модель для таблицы keyword_stats в PostgreSQL.
    Хранит агрегированную статистику по ключевым словам для рекламных кампаний.
    """
    __tablename__ = "keyword_stats"
    id = Column(Integer, primary_key=True, autoincrement=True)
    advert_id = Column(Integer, nullable=False, index=True)
    nm_id = Column(Integer, nullable=False, index=True)
    start_date = Column(Date, nullable=False, index=True)
    send_time = Column(Time, nullable=False, index=True)
    atbs = Column(Integer, nullable=True)
    avg_pos = Column(Numeric(precision=10, scale=2), nullable=True)
    clicks = Column(Integer, nullable=True)
    cpc = Column(Numeric(precision=8, scale=2), nullable=True)
    cpm = Column(Numeric(precision=8, scale=2), nullable=True)
    ctr = Column(Numeric(precision=8, scale=2), nullable=True)
    norm_query = Column(String, nullable=False, index=True)
    orders = Column(Integer, nullable=True)
    shks = Column(Integer, nullable=True)
    views = Column(Integer, nullable=True)

    __table_args__ = (
        Index("uq_advert_date_keyword",
              "advert_id", "nm_id", "start_date", "send_time",  "norm_query",
              unique=True),
    )