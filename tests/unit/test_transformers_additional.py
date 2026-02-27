"""
Дополнительные тесты для трансформеров OrdersTransformer и SalesFunnelTransformer,
покрывают успешные варианты, ошибки типов и поддержку моделей.
"""

import pytest
from datetime import datetime

from src.transformers.orders import OrdersTransformer
from src.transformers.sales_funnel import SalesFunnelTransformer
from src.schemas.api_schemas.orders import Order
from src.schemas.api_schemas.sales_funnel import SalesFunnel, Product, History


def test_orders_transformer_success():
    transformer = OrdersTransformer()
    dt = datetime(2025, 1, 2, 3, 4, 5)
    last = datetime(2025, 1, 3, 4, 5, 6)
    cancel = datetime(2025, 1, 4, 5, 6, 7)
    record = {
        "date_release": dt,
        "lastChangeDate": last,
        "warehouseName": "W",
        "warehouseType": "T",
        "countryName": "C",
        "oblastOkrugName": "O",
        "regionName": "R",
        "supplierArticle": "SA",
        "nmId": 123,
        "barcode": "B",
        "category": "Cat",
        "subject": "Sub",
        "techSize": "TS",
        "incomeID": 1,
        "isSupply": True,
        "isRealization": False,
        "totalPrice": 10.0,
        "discountPercent": 5,
        "spp": 1.0,
        "finishedPrice": 8.0,
        "priceWithDisc": 7.0,
        "cancelDate": cancel,
        "sticker": "S",
        "gNumber": "G",
        "srid": "SR",
    }

    output = transformer.transform([record])
    assert isinstance(output, list) and len(output) == 1
    row = output[0]
    assert row["date_release"] == dt.date()
    assert row["time_release"] == dt.time()
    assert row["lastChangeDate"] == last.date()
    assert row["cancelDate"] == cancel.date()


def test_orders_transformer_type_error():
    transformer = OrdersTransformer()
    with pytest.raises(TypeError):
        transformer.transform("not a list")


def test_orders_transformer_string_dates():
    transformer = OrdersTransformer()
    rec = {"date_release": "2025-01-02T03:04:05",
           "lastChangeDate": "2025-01-03T04:05:06",
           "warehouseName": "W", "warehouseType": "T",
           "countryName": "C", "oblastOkrugName": "O",
           "regionName": "R", "supplierArticle": "SA",
           "nmId": 123, "barcode": "B", "category": "Cat",
           "subject": "Sub", "techSize": "TS", "incomeID": 1,
           "isSupply": True, "isRealization": False,
           "totalPrice": 10.0, "discountPercent": 5,
           "spp": 1.0, "finishedPrice": 8.0, "priceWithDisc": 7.0,
           "cancelDate": "0001-01-01T00:00:00",  # нулевая дата должна стать None
           "sticker": "S", "gNumber": "G", "srid": "SR"}
    out = transformer.transform([rec])
    assert out[0]["date_release"] == datetime(2025,1,2,3,4,5).date()
    assert out[0]["cancelDate"] is None


def test_orders_transformer_accepts_model_instance():
    transformer = OrdersTransformer()
    dt = datetime(2025, 1, 2, 3, 4, 5)
    last = datetime(2025, 1, 3, 4, 5, 6)
    cancel = datetime(2025, 1, 4, 5, 6, 7)
    rec = {
        "date_release": dt,
        "lastChangeDate": last,
        "warehouseName": "W",
        "warehouseType": "T",
        "countryName": "C",
        "oblastOkrugName": "O",
        "regionName": "R",
        "supplierArticle": "SA",
        "nmId": 123,
        "barcode": "B",
        "category": "Cat",
        "subject": "Sub",
        "techSize": "TS",
        "incomeID": 1,
        "isSupply": True,
        "isRealization": False,
        "totalPrice": 10.0,
        "discountPercent": 5,
        "spp": 1.0,
        "finishedPrice": 8.0,
        "priceWithDisc": 7.0,
        "cancelDate": cancel,
        "sticker": "S",
        "gNumber": "G",
        "srid": "SR",
    }
    order_obj = Order(**rec)
    output = transformer.transform([order_obj])
    assert output[0]["srid"] == "SR"
    # убедиться, что поля даты всё ещё конвертируются
    assert output[0]["date_release"] == dt.date()


def make_sales_item():
    # создаём объект SalesFunnel
    prod = Product(
        nmId=10,
        title="T",
        vendorCode="V",
        brandName="B",
        subjectId=1,
        subjectName="SN",
    )
    hist = History(
        date=datetime(2025, 2, 2, 0, 0, 0),
        openCount=1,
        cartCount=2,
        orderCount=3,
        orderSum=4,
        buyoutCount=5,
        buyoutSum=6,
        buyoutPercent=7,
        addToCartConversion=8,
        cartToOrderConversion=9,
        addToWishlistCount=10,
    )
    return SalesFunnel(product=prod, history=hist, currency="RUB")


def test_sales_funnel_transformer_success():
    transformer = SalesFunnelTransformer()
    sf = make_sales_item()
    out = transformer.transform([sf])
    assert len(out) == 1
    rec = out[0]
    assert rec["nmId"] == 10
    assert rec["title"] == "T"
    assert rec["date_release"] == sf.history.date.date()


def test_sales_funnel_transformer_accepts_dict():
    transformer = SalesFunnelTransformer()
    sf = make_sales_item()
    # преобразуем в словарь и проверяем, что трансформация аналогична
    rec_dict = sf.model_dump(mode="json")
    out = transformer.transform([rec_dict])
    assert out[0]["nmId"] == 10


def test_sales_funnel_transformer_type_error():
    transformer = SalesFunnelTransformer()
    with pytest.raises(TypeError):
        transformer.transform("nope")
