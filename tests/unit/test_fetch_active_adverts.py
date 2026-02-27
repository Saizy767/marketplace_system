"""
Тесты оператора FetchActiveAdvertsOperator.
Проверяют поведение при нормальном ответе, пустом результате, http-ошибках и ошибках валидации.
"""

import pytest
from src.operators.fetch_active_adverts import FetchActiveAdvertsOperator
from src.schemas.api_schemas.active_adverts import ActiveAdvertsResponse



@pytest.fixture
# пример полезной нагрузки, которую возвращает внешний API
# содержит рекламные кампании с разными статусами

def mock_api_response():
    return {
        "adverts": [
            {"id": 19128432, "status": 9, "bid_type": "manual", "nm_settings": [],
             "settings": {"name": "Test Campaign", "payment_type": "daily", "placements": {"search": True, "recommendations": False}},
             "timestamps": {"created": "2025-01-01T00:00:00", "deleted": "2025-01-01T00:00:00", "updated": "2025-01-01T00:00:00"}},
            {"id": 25976117, "status": 9, "bid_type": "manual", "nm_settings": [],
             "settings": {"name": "Another Campaign", "payment_type": "weekly", "placements": {"search": True, "recommendations": True}},
             "timestamps": {"created": "2025-01-01T00:00:00", "deleted": "2025-01-01T00:00:00", "updated": "2025-01-01T00:00:00"}},
            {"id": 19107227, "status": 7, "bid_type": "manual", "nm_settings": [],
             "settings": {"name": "Inactive Campaign", "payment_type": "daily", "placements": {"search": False, "recommendations": False}},
             "timestamps": {"created": "2025-01-01T00:00:00", "deleted": "2025-01-01T00:00:00", "updated": "2025-01-01T00:00:00"}},
            {"id": 11740375, "status": 11, "bid_type": "unified", "nm_settings": [],
             "settings": {"name": "Unified Campaign", "payment_type": "monthly", "placements": {"search": True, "recommendations": True}},
             "timestamps": {"created": "2025-01-01T00:00:00", "deleted": "2025-01-01T00:00:00", "updated": "2025-01-01T00:00:00"}}
        ]
    }


def test_fetch_active_adverts_operator_success(requests_mock, mock_api_response):
    # успешный запрос: должны вернуть только записи со статусом 9
    import src.config.endpoints as eps
    url = eps.get_endpoints().ACTIVE_ADVERTS
    requests_mock.get(url, json=mock_api_response)

    operator = FetchActiveAdvertsOperator(task_id="test_fetch")
    context = {}

    result = operator.execute(context)

    valid = ActiveAdvertsResponse.model_validate(mock_api_response)
    expected = [a.model_dump(mode="json") for a in valid.adverts if a.status == 9]
    assert result == expected


def test_fetch_active_adverts_operator_empty_response(requests_mock):
    # если API возвращает пустой список, оператор выдаёт пустой результат
    import src.config.endpoints as eps
    url = eps.get_endpoints().ACTIVE_ADVERTS
    requests_mock.get(url, json={"adverts": []})

    operator = FetchActiveAdvertsOperator(task_id="test_fetch")
    result = operator.execute({})
    assert result == []
    assert isinstance(ActiveAdvertsResponse.model_validate({"adverts": []}), ActiveAdvertsResponse)


def test_fetch_active_adverts_operator_http_error(requests_mock):
    # HTTP 500 приводит к RuntimeError
    import src.config.endpoints as eps
    url = eps.get_endpoints().ACTIVE_ADVERTS
    requests_mock.get(url, status_code=500, json={"error": "oops"})

    operator = FetchActiveAdvertsOperator(task_id="test_fetch")
    with pytest.raises(RuntimeError):
        operator.execute({})


def test_fetch_active_adverts_operator_validation_error(requests_mock):
    # если ответ не соответствует схеме, бросаем RuntimeError
    import src.config.endpoints as eps
    url = eps.get_endpoints().ACTIVE_ADVERTS
    requests_mock.get(url, json={"foo": "bar"})

    operator = FetchActiveAdvertsOperator(task_id="test_fetch")
    with pytest.raises(RuntimeError):
        operator.execute({})
