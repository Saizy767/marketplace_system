from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    Date, 
    Time,
    Index,
    Numeric,
    )
from src.tables.base import Base

class Orders(Base):
    '''
    ORM-модель для таблицы orders в PostgreSQL.
    Хранит информацию о заказах поставщика.
    '''
    __tablename__ = "orders"
    date_release = Column(Date, nullable=False, index=True)
    time_release = Column(Time, nullable=True, index=False)
    lastChangeDate = Column(Date, nullable=True, index=False)
    warehouseName = Column(String, nullable=True, index=False)
    warehouseType = Column(String, nullable=True, index=False)
    countryName = Column(String, nullable=True, index=False)
    oblastOkrugName = Column(String, nullable=True, index=False)
    regionName = Column(String, nullable=True, index=False)
    supplierArticle = Column(String, nullable=True, index=False)
    nmId = Column(Integer, nullable=True, index=False)
    barcode = Column(String, nullable=True, index=False)
    category = Column(String, nullable=True, index=False)
    subject = Column(String, nullable=True, index=False)
    techSize = Column(String, nullable=True, index=False)
    incomeID = Column(Integer, nullable=True, index=False)
    isSupply = Column(String, nullable=True, index=False)
    isRealization = Column(String, nullable=True, index=False)
    totalPrice = Column(Numeric(precision=10, scale=2), nullable=True, index=False)
    discountPercent = Column(Integer, nullable=True, index=False)
    spp = Column(Numeric(precision=10, scale=2), nullable=True, index=False)
    finishedPrice = Column(Numeric(precision=10, scale=2), nullable=True, index=False)
    priceWithDisc = Column(Numeric(precision=10, scale=2), nullable=True, index=False)
    cancelDate = Column(Date, nullable=True, index=False)
    sticker = Column(String, nullable=True, index=False)
    gNumber = Column(String, nullable=True, index=False)
    srid = Column(String, primary_key=True, index=True)

    __table_args__ = (
        Index(
            "uq_date_release_srid",
            "date_release",
            "srid",
            unique=True),
    )