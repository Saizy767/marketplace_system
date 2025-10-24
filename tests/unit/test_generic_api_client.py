import pytest
from unittest.mock import Mock
import requests
from src.api_client.generic import GenericApiClient
from src.schemas.api_schemas.stats_keywords import StatResponse


def test_fetch_data_valid_response_with_model(mocker):
    mock_response = Mock()
    mock_response.json.return_value = {
        "stat": [
            {
                "begin": "2025-10-14T00:00:00",
                "end": "2025-10-14T23:59:59",
                "keyword": "телефон",
                "campaignName": "Кампания",
                "advertId": 123,
                "views": 100,
                "clicks": 10,
                "ctr": 0.1,
                "cpc": 15.0,
                "duration": 86400,
                "sum": 1500.0,
                "frq": 1.0
            }
        ]
    }
    mock_response.raise_for_status = Mock()
    mocker.patch("src.api_client.generic.requests.get", return_value=mock_response)
    client = GenericApiClient(timeout=5)
    result = client.fetch_data(
        url="https://api.example.com/test",
        response_model=StatResponse
    )
    assert isinstance(result, StatResponse)
    assert len(result.stat) == 1
    

def test_fetch_data_http_error(mocker):
    mocker.patch(
        "src.api_client.generic.requests.get",
        side_effect=requests.RequestException("Network error")
    )
    client = GenericApiClient(timeout=1)
    with pytest.raises(RuntimeError, match="HTTP request failed"):
        client.fetch_data(url="https://api.example.com/test")