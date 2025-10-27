from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    Float, 
    Date, 
    UniqueConstraint,
    Time)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB 

Base = declarative_base()

class KeywordStat(Base):
    __tablename__ = "keyword_stats"
    id = Column(Integer, primary_key=True, autoincrement=True)
    advert_id = Column(String, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    send_time = Column(Time, nullable=False, index=True)
    info_keywords = Column(JSONB, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "advert_id", "date", "send_time", "info_keywords",
            name="uq_advert_date_keyword"),
    )