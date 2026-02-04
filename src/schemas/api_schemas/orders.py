from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class Order(BaseModel):
    date_release: datetime
    lastChangeDate: datetime
    warehouseName: str
    warehouseType: str
    countryName: str
    oblastOkrugName: str
    regionName: str
    supplierArticle: str
    nmId: int
    barcode: str
    category: str
    subject: str
    techSize: str
    incomeID: int
    isSupply: str
    isRealization: str
    totalPrice: float
    discountPercent: int
    spp: float
    finishedPrice: float
    priceWithDisc: float
    cancelDate: datetime
    sticker: str
    gNumber: str
    srid: str