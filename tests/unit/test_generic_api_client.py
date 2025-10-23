import pytest
from unittest.mock import Mock
import requests
from src.api_client.generic import GenericApiClient
from src.schemas.api_schemas.stats_keywords import KeywordListResponse

def test_fetch_data_valid_response_with_model(mocker):
    mock_response = Mock()
    mock_response.json.return_value = {
        "keywords": [{"date": "2025-10-14", "stats": []}]
    }
    mock_response.raise_for_status = Mock()
    mocker.patch("src.api_client.generic.requests.get", return_value=mock_response)

    client = GenericApiClient(timeout=5)
    result = client.fetch_data(
        url="https://api.example.com/test",
        response_model=KeywordListResponse
    )

    assert isinstance(result, KeywordListResponse)
    assert len(result.keywords) == 1

def test_fetch_data_http_error(mocker):
    mocker.patch(
        "src.api_client.generic.requests.get",
        side_effect=requests.RequestException("Network error")
    )
    client = GenericApiClient(timeout=1)
    with pytest.raises(RuntimeError, match="HTTP request failed"):
        client.fetch_data(url="https://api.example.com/test")