from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    Date,
    Index,
    Numeric,
    )
from src.tables.base import Base

class SalesFunnelTable(Base):
    '''
    ORM-модель для таблицы sales_funnel в PostgreSQL.
    Хранит информацию о воронке продаж.
    '''
    __tablename__ = "sales_funnel"
    nmId = Column(Integer, nullable=False, index=True)
    title = Column(String, nullable=False)
    vendorCode = Column(String, nullable=False)
    date_release = Column(Date, nullable=False, index=True)
    openCount = Column(Integer, nullable=False)
    cartCount = Column(Integer, nullable=False)
    orderCount = Column(Integer, nullable=False)
    orderSum = Column(Numeric(precision=10, scale=2), nullable=False)
    buyoutCount = Column(Integer, nullable=False)
    buyoutSum = Column(Numeric(precision=10, scale=2), nullable=False)
    buyoutPercent = Column(Numeric(precision=5, scale=2), nullable=False)
    addToCartConversion = Column(Integer, nullable=False)
    cartToOrderConversion = Column(Integer, nullable=False)
    addToWishlistCount = Column(Integer, nullable=False)

    __table_args__ = (
        Index(
            "uq_date_release_nmid",
            "nmId",
            "date_release",
            unique=True),
    )