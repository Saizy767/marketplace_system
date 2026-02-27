"""
Дополнительные проверки GenericApiClient, которые не поместились в основной тестовый файл.
Проверяются заголовки авторизации, ошибки, валидация и поддержка списков.
"""

import pytest
from src.api_client.generic import GenericApiClient
from pydantic import BaseModel
from src.config import settings


def test_fetch_data_adds_bearer_header(requests_mock, monkeypatch):
    # при отсутствии схемы токена добавляется префикс Bearer из настроек
    monkeypatch.setattr(settings.Variable, "get", lambda k: "secret123")
    url = "http://example.com/foobar"
    def matcher(request):
        return request.headers.get("Authorization") == "Bearer secret123"
    requests_mock.get(url, additional_matcher=matcher, json={"foo": "bar"})
    client = GenericApiClient()
    data = client.fetch_data(url=url)
    assert data == {"foo": "bar"}


def test_fetch_data_preserves_bearer_prefix(requests_mock, monkeypatch):
    # если токен уже содержит 'Bearer', он не изменяется
    monkeypatch.setattr(settings.Variable, "get", lambda k: "Bearer xyz")
    url = "http://example.com/abc"
    def matcher(request):
        return request.headers.get("Authorization") == "Bearer xyz"
    requests_mock.get(url, additional_matcher=matcher, json={"a": 1})
    client = GenericApiClient()
    data = client.fetch_data(url=url)
    assert data == {"a": 1}


def test_fetch_data_http_error_raises(requests_mock, monkeypatch):
    # при HTTP-ошибке метод должен бросать RuntimeError
    monkeypatch.setattr(settings.Variable, "get", lambda k: "t")
    url = "http://example.com/err"
    requests_mock.get(url, status_code=500)
    client = GenericApiClient()
    with pytest.raises(RuntimeError, match="HTTP request failed"):
        client.fetch_data(url=url)


def test_fetch_data_invalid_json(requests_mock, monkeypatch):
    # некорректный JSON тоже рассматривается как ошибка запроса
    monkeypatch.setattr(settings.Variable, "get", lambda k: "t")
    url = "http://example.com/bad"
    requests_mock.get(url, text="not json")
    client = GenericApiClient()
    with pytest.raises(RuntimeError, match="HTTP request failed"):
        client.fetch_data(url=url)


def test_fetch_data_validation_failure(requests_mock, monkeypatch):
    # если модель валидации не проходит, бросаем RuntimeError
    monkeypatch.setattr(settings.Variable, "get", lambda k: "t")
    class Simple(BaseModel):
        x: int
    url = "http://example.com/val"
    requests_mock.get(url, json={"x": "notint"})
    client = GenericApiClient()
    with pytest.raises(RuntimeError, match="Response validation failed"):
        client.fetch_data(url=url, response_model=Simple)


def test_fetch_data_list_model_support(requests_mock, monkeypatch):
    # поддержка response_model=list[Model]
    monkeypatch.setattr(settings.Variable, "get", lambda k: "t")
    class Item(BaseModel):
        name: str
    url = "http://example.com/list"
    requests_mock.get(url, json=[{"name": "foo"}, {"name": "bar"}])
    client = GenericApiClient()
    result = client.fetch_data(url=url, response_model=list[Item])
    assert isinstance(result, list) and result[0].name == "foo"


def test_fetch_data_orders_special_case(requests_mock, monkeypatch):
    # специальная логика для OrdersResponse, должна вернуть экземпляр класса
    from src.schemas.api_schemas.orders import OrdersResponse
    monkeypatch.setattr(settings.Variable, "get", lambda k: "t")
    url = "http://example.com/orders"
    record = {
        "date_release": "2025-01-01T00:00:00",
        "lastChangeDate": "2025-01-02T00:00:00",
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
        "cancelDate": None,
        "sticker": "S",
        "gNumber": "G",
        "srid": "SR",
    }
    requests_mock.get(url, json=[record])
    client = GenericApiClient()
    out = client.fetch_data(url=url, response_model=OrdersResponse)
    assert isinstance(out, OrdersResponse)
    assert out.orders[0].srid == "SR"


def test_post_data_validation_and_error(requests_mock, monkeypatch):
    # POST-метод: сначала проверка валидации ответа, затем нормальная отправка
    monkeypatch.setattr(settings.Variable, "get", lambda k: "t")
    url = "http://example.com/post"
    requests_mock.post(url, json={"a": "a"})
    class Foo(BaseModel):
        a: int
    client = GenericApiClient()
    with pytest.raises(RuntimeError, match="Response validation failed"):
        client.post_data(url=url, json={"a": "a"}, response_model=Foo)
    def matchreq(r):
        return r.headers.get("Authorization") == "Bearer t"
    requests_mock.post(url, additional_matcher=matchreq, json={"ok": True})
    result = client.post_data(url=url, json={"ok": True})
    assert result == {"ok": True}
