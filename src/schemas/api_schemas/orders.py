from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field, field_validator


class Order(BaseModel):
    date_release: Optional[datetime] = Field(None, alias="date")
    lastChangeDate: Optional[datetime]
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
    brand: Optional[str] = None
    techSize: str
    incomeID: int
    # API sometimes returns booleans here — normalize to strings
    isSupply: Optional[str]
    isRealization: Optional[str]
    totalPrice: float
    discountPercent: int
    spp: float
    finishedPrice: float
    priceWithDisc: float
    isCancel: Optional[bool] = None
    cancelDate: Optional[datetime]
    sticker: Optional[str]
    gNumber: str
    srid: str

    model_config = {"populate_by_name": True, "extra": "ignore"}

    @field_validator("date_release", "lastChangeDate", "cancelDate", mode="before")
    def _parse_maybe_wrapped_date(cls, v: Any):
        if v is None:
            return None
        # API may return {'date': '2026-02-08T...'} or an ISO string
        if isinstance(v, dict) and "date" in v:
            s = v["date"]
        else:
            s = v
        if isinstance(s, str):
            # handle zero-date and trailing Z
            if s.startswith("0001-01-01"):
                return None
            s2 = s.replace("Z", "+00:00")
            try:
                return datetime.fromisoformat(s2)
            except Exception:
                return None
        return v

    @field_validator("isSupply", "isRealization", mode="before")
    def _coerce_bool_to_str(cls, v: Any):
        if v is None:
            return None
        if isinstance(v, bool):
            return "True" if v else "False"
        return str(v)


class OrdersResponse(BaseModel):
    """
    Модель ответа API для списка заказов.
    """
    orders: List[Order]

    @field_validator("orders", mode="before")
    def ensure_orders_list(cls, v: Any):
        # Accept either a top-level list, or a dict with 'orders' key
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, dict) and "orders" in v:
            return v["orders"]
        return v