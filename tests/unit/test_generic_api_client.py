"""
Основные тесты для GenericApiClient: проверка валидации, ошибок и возврата
сырых данных.
"""

import pytest
import requests
from src.api_client.generic import GenericApiClient
from src.schemas.api_schemas.stats_keywords import StatsResponse


def test_fetch_data_valid_response_with_model(requests_mock):
    # возвращается экземпляр response_model при корректных данных
    payload = {
        "stat": [
            {
                "advert_id": 1,
                "nm_id": 2,
                "stats": [
                    {
                        "atbs": 0,
                        "avg_pos": 1.0,
                        "clicks": 1,
                        "cpc": 5.0,
                        "cpm": 0.0,
                        "ctr": 0.1,
                        "norm_query": "телефон",
                        "orders": 0,
                        "shks": 0,
                        "views": 10,
                        "spend": 50,
                    }
                ],
            }
        ]
    }
    requests_mock.get("https://api.test.com/foo", json=payload)

    client = GenericApiClient(timeout=5)
    result = client.fetch_data(url="https://api.test.com/foo", response_model=StatsResponse)
    assert isinstance(result, StatsResponse)
    assert len(result.stat) == 1


def test_fetch_data_validation_error(requests_mock):
    # если валидация провалилась, падает RuntimeError
    bad = {"foobar": 123}
    requests_mock.get("https://api.test.com/foo", json=bad)
    client = GenericApiClient(timeout=5)
    with pytest.raises(RuntimeError, match="Response validation failed"):
        client.fetch_data(url="https://api.test.com/foo", response_model=StatsResponse)


def test_fetch_data_no_model_returns_raw(requests_mock):
    # без model возвращается необработанный JSON
    payload = {"a": 1}
    requests_mock.get("https://api.test.com/foo", json=payload)
    client = GenericApiClient(timeout=5)
    assert client.fetch_data(url="https://api.test.com/foo") == payload


def test_fetch_data_http_error(requests_mock):
    # ошибки библиотеки requests интерпретируются как RuntimeError
    requests_mock.get("https://api.test.com/foo", exc=requests.RequestException("oops"))
    client = GenericApiClient(timeout=5)
    with pytest.raises(RuntimeError, match="HTTP request failed"):
        client.fetch_data(url="https://api.test.com/foo")
