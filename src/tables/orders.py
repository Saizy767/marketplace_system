from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    Date, 
    Index,
    Numeric,
    Time)
from src.tables.base import Base

class Orders(Base):
    '''
    ORM-модель для таблицы orders в PostgreSQL.
    Хранит информацию о заказах поставщика.
    '''
    __tablename__ = "orders"
    date_release = Column(Date, nullable=False, index=False)
    lastChangeDate = Column(Date, nullable=False, index=False)
    warehouseName = Column(String, nullable=False, index=False)
    warehouseType = Column(String, nullable=False, index=False)
    countryName = Column(String, nullable=False, index=False)
    oblastOkrugName = Column(String, nullable=False, index=False)
    regionName = Column(String, nullable=False, index=False)
    supplierArticle = Column(String, nullable=False, index=False)
    nmId = Column(Integer, nullable=False, index=False)
    barcode = Column(String, nullable=False, index=False)
    category = Column(String, nullable=False, index=False)
    subject = Column(String, nullable=False, index=False)
    techSize = Column(String, nullable=False, index=False)
    incomeID = Column(Integer, nullable=False, index=False)
    isSupply = Column(String, nullable=False, index=False)
    isRealization = Column(String, nullable=False, index=False)
    totalPrice = Column(Numeric(precision=10, scale=2), nullable=False, index=False)
    discountPercent = Column(Integer, nullable=False, index=False)
    spp = Column(Numeric(precision=10, scale=2), nullable=False, index=False)
    finishedPrice = Column(Numeric(precision=10, scale=2), nullable=False, index=False)
    priceWithDisc = Column(Numeric(precision=10, scale=2), nullable=False, index=False)
    cancelDate = Column(Date, nullable=False, index=False)
    sticker = Column(String, nullable=False, index=False)
    gNumber = Column(String, nullable=False, index=False)
    srid = Column(String, nullable=False, index=True)

    __table_args__ = (
        Index("uq_srid",
              "srid",
              unique=True),
    )