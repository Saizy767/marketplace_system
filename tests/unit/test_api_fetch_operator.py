"""
Юнит‑тесты для ApiFetchOperator. Проверяется получение и валидация данных,
а также поведение при ошибках.
"""

import pytest
from src.operators.api_fetch import ApiFetchOperator
from src.schemas.api_schemas.stats_keywords import StatsResponse


def test_execute_returns_serialized_data(requests_mock):
    # оператор возвращает распарсенный JSON без модификаций
    url = "http://example"
    requests_mock.get(url, json={"stat": []})

    op = ApiFetchOperator(task_id="t", url=url, params={"x":1})
    result = op.execute({})
    assert isinstance(result, dict)
    assert "stat" in result


def test_execute_validates_response(requests_mock):
    # успешная валидация через StatsResponse
    url = "http://example"
    payload = {
        "stat": [
            {
                "advert_id": 7,
                "nm_id": 42,
                "stats": [
                    {
                        "atbs": 1,
                        "avg_pos": 2.5,
                        "clicks": 3,
                        "cpc": 1.2,
                        "cpm": 0.5,
                        "ctr": 10.0,
                        "norm_query": "foo",
                        "orders": 0,
                        "shks": 5,
                        "views": 100,
                        "spend": 123,
                    }
                ],
            }
        ]
    }
    requests_mock.get(url, json=payload)

    op = ApiFetchOperator(task_id="t", url=url)
    result = op.execute({})
    expected = StatsResponse.model_validate(payload).model_dump()
    assert result == expected


def test_execute_validation_error(requests_mock):
    # если модель не валидируется, выбрасываем Exception
    url = "http://example"
    requests_mock.get(url, json={"stat": [{"advert_id": 1}]})

    op = ApiFetchOperator(task_id="t", url=url)
    with pytest.raises(Exception):
        op.execute({})


def test_execute_propagates_error(requests_mock):
    # HTTP-ошибка трансформируется в RuntimeError
    url = "http://example"
    requests_mock.get(url, status_code=500)

    op = ApiFetchOperator(task_id="t", url=url)
    with pytest.raises(RuntimeError):
        op.execute({})
