import pytest
import requests_mock
from src.api_client.generic import GenericApiClient
from src.schemas.api_schemas.stats_keywords import StatsResponse
from src.config import endpoints

# УБЕРИТЕ импорт Settings и settings = Settings()

@pytest.fixture(autouse=True)
def mock_airflow_variables(mocker):
    mocker.patch(
        "airflow.models.Variable.get",
        side_effect=lambda key, default=None: {
            "API_KEY": "test-key",
            "API_BASE_URL": "https://mock-api.com",
        }[key]
    )

def test_full_api_call_mocked():
    with requests_mock.Mocker() as m:
        # УБЕРИТЕ лишние пробелы в URL!
        m.get(
            "https://mock-api.com/adv/v1/stat/words",
            json={
                "stat": [{
                    "begin": "2025-10-14T00:00:00",
                    "end": "2025-10-14T23:59:59",
                    "keyword": "телефон",
                    "campaignName": "Кампания 1",
                    "advertId": 123,
                    "views": 100,
                    "clicks": 10,
                    "ctr": 0.1,
                    "cpc": 15.0,
                    "duration": 86400,
                    "sum": 1500.0,
                    "frq": 1.0
                }],
                "fixed": True
            },
            status_code=200
        )

        client = GenericApiClient(timeout=10)
        # Теперь endpoints автоматически получат mock-значения
        url = endpoints.get_endpoints().STATISTIC_WORDS
        response = client.fetch_data(
            url=url,
            params={"id": "123", "from": "2025-10-01", "to": "2025-10-02"},
            response_model=StatsResponse
        )
        assert isinstance(response, StatsResponse)
        assert len(response.stat) == 1