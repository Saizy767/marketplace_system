import pytest
from unittest.mock import Mock
from src.operators.fetch_active_adverts import FetchActiveAdvertsOperator
from src.schemas.api_schemas.active_adverts import ActiveAdvertsResponse
from unittest import mock

with mock.patch("airflow.models.Variable.get") as mock_get:
    mock_get.side_effect = lambda key, default=None: {
        "API_KEY": "test-api-key",
        "API_BASE_URL": "https://api.test.com",
    }.get(key, default)


@pytest.fixture
def mock_api_response():
    return {
        "adverts": [
            {
                "id": 19128432,
                "status": 9,
                "bid_type": "manual",
                "nm_settings": [],
                "settings": {
                    "name": "Test Campaign",
                    "payment_type": "daily",
                    "placements": {"search": True, "recommendations": False}
                },
                "timestamps": {
                    "created": "2025-01-01T00:00:00",
                    "deleted": "2025-01-01T00:00:00",
                    "updated": "2025-01-01T00:00:00"
                }
            },
            {
                "id": 25976117,
                "status": 9,
                "bid_type": "manual",
                "nm_settings": [],
                "settings": {
                    "name": "Another Campaign",
                    "payment_type": "weekly",
                    "placements": {"search": True, "recommendations": True}
                },
                "timestamps": {
                    "created": "2025-01-01T00:00:00",
                    "deleted": "2025-01-01T00:00:00",
                    "updated": "2025-01-01T00:00:00"
                }
            },
            {
                "id": 19107227,
                "status": 7,
                "bid_type": "manual",
                "nm_settings": [],
                "settings": {
                    "name": "Inactive Campaign",
                    "payment_type": "daily",
                    "placements": {"search": False, "recommendations": False}
                },
                "timestamps": {
                    "created": "2025-01-01T00:00:00",
                    "deleted": "2025-01-01T00:00:00",
                    "updated": "2025-01-01T00:00:00"
                }
            },
            {
                "id": 11740375,
                "status": 11,
                "bid_type": "unified",
                "nm_settings": [],
                "settings": {
                    "name": "Unified Campaign",
                    "payment_type": "monthly",
                    "placements": {"search": True, "recommendations": True}
                },
                "timestamps": {
                    "created": "2025-01-01T00:00:00",
                    "deleted": "2025-01-01T00:00:00",
                    "updated": "2025-01-01T00:00:00"
                }
            }
        ]
    }

def test_fetch_active_adverts_operator_success(mocker, mock_api_response):
    # Arrange
    mock_client = mocker.patch("src.operators.fetch_active_adverts.GenericApiClient")
    mock_instance = Mock()
    mock_instance.fetch_data.return_value = ActiveAdvertsResponse.model_validate(mock_api_response)
    mock_client.return_value = mock_instance

    operator = FetchActiveAdvertsOperator(task_id="test_fetch")
    context = {}

    # Act
    result = operator.execute(context)

    # Assert
    assert result == [19128432, 25976117]
    mock_instance.fetch_data.assert_called_once()
    call_kwargs = mock_instance.fetch_data.call_args.kwargs
    assert call_kwargs["response_model"] == ActiveAdvertsResponse


def test_fetch_active_adverts_operator_empty_response(mocker):
    mock_client = mocker.patch("src.operators.fetch_active_adverts.GenericApiClient")
    mock_instance = Mock()
    mock_instance.fetch_data.return_value = ActiveAdvertsResponse(adverts=[])
    mock_client.return_value = mock_instance

    operator = FetchActiveAdvertsOperator(task_id="test_fetch")
    result = operator.execute({})
    assert result == []


def test_fetch_active_adverts_operator_http_error(mocker):
    mock_client = mocker.patch("src.operators.fetch_active_adverts.GenericApiClient")
    mock_instance = Mock()
    mock_instance.fetch_data.side_effect = RuntimeError("HTTP request failed")
    mock_client.return_value = mock_instance

    operator = FetchActiveAdvertsOperator(task_id="test_fetch")
    with pytest.raises(RuntimeError, match="HTTP request failed"):
        operator.execute({})


def test_fetch_active_adverts_operator_validation_error(mocker):
    mock_client = mocker.patch("src.operators.fetch_active_adverts.GenericApiClient")
    mock_instance = Mock()
    mock_instance.fetch_data.side_effect = RuntimeError("Response validation failed")
    mock_client.return_value = mock_instance

    operator = FetchActiveAdvertsOperator(task_id="test_fetch")
    with pytest.raises(RuntimeError, match="Response validation failed"):
        operator.execute({})