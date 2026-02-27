import pytest
import requests_mock
from src.api_client.generic import GenericApiClient
from src.schemas.api_schemas.stats_keywords import StatsResponse
from src.config import endpoints

@pytest.fixture(autouse=True)
def mock_airflow_variables(mocker):
    mocker.patch(
        "airflow.models.Variable.get",
        side_effect=lambda key, default=None: {
            "API_KEY": "test-key",
            "API_BASE_URL": "https://mock-api.com",
            "API_STATISTIC_URL": "https://mock-api.com/adv/v1/stat/words",
            "API_SELLER_URL": "https://mock-api.com/seller",
        }[key]
    )

def test_full_api_call_mocked():
    with requests_mock.Mocker() as m:
        m.get(
            "https://mock-api.com/adv/v0/normquery/stats",
            json={
                "stat": [
                    {
                        "advert_id": 123,
                        "nm_id": 456,
                        "stats": [
                            {
                                "atbs": 0,
                                "avg_pos": 1.0,
                                "clicks": 10,
                                "cpc": 15.0,
                                "cpm": 0.0,
                                "ctr": 0.1,
                                "norm_query": "телефон",
                                "orders": 1,
                                "shks": 1,
                                "views": 100,
                                "spend": 1500
                            }
                        ]
                    }
                ],
                "fixed": True
            },
            status_code=200
        )

        client = GenericApiClient(timeout=10)
        url = endpoints.get_endpoints().STATISTIC_WORDS
        response = client.fetch_data(
            url=url,
            params={"id": "123", "from": "2025-10-01", "to": "2025-10-02"},
            response_model=StatsResponse
        )
        assert isinstance(response, StatsResponse)
        assert len(response.stat) == 1