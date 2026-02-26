from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field, field_validator


class Order(BaseModel):
    date_release: Optional[datetime] = Field(None, alias="date", description="Дата и время заказа")
    lastChangeDate: Optional[datetime] = Field(..., description="Дата и время обновления информации в сервисе")
    warehouseName: str = Field(..., description="Склад отгрузки")
    warehouseType: str = Field(..., description="Тип склада хранения товаров")
    countryName: str = Field(..., description="Страна")
    oblastOkrugName: str = Field(..., description="Округ")
    regionName: str = Field(..., description="Регион")
    supplierArticle: str = Field(..., description="Артикул продавца")
    nmId: int = Field(..., description="Артикул WB")
    barcode: str = Field(..., description="Баркод")
    category: str = Field(..., description="Категория")
    subject: str = Field(..., description="Предмет")
    brand: Optional[str] = Field(None, description="Бренд")
    techSize: str = Field(..., description="Размер товара")
    incomeID: int = Field(..., description="Номер поставки")
    isSupply: Optional[str] = Field(..., description="Договор поставки")
    isRealization: Optional[str] = Field(..., description="Договор реализации")
    totalPrice: float = Field(..., description="Цена без скидок")
    discountPercent: int = Field(..., description="Скидка продавца, %")
    spp: float = Field(..., description="Скидка WB, %")
    finishedPrice: float = Field(..., description="Цена с учетом всех скидок, кроме суммы по WB Кошельку")
    priceWithDisc: float = Field(..., description="Цена со скидкой продавца, в том числе со скидкой WB Клуба")
    isCancel: Optional[bool] = Field(None, description="Отмена заказа")
    cancelDate: Optional[datetime] = Field(..., description="Дата и время отмены заказа")
    sticker: Optional[str] = Field(..., description="ID стикера")
    gNumber: str = Field(..., description="ID корзины покупателя")
    srid: str = Field(..., description="Уникальный ID заказа")

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