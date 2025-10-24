import requests_mock
from src.api_client.generic import GenericApiClient
from src.schemas.api_schemas.stats_keywords import StatResponse
from src.config.settings import settings

def test_full_api_call_mocked():
    with requests_mock.Mocker() as m:
        m.get(
            "https://mock-api.com/adv/v1/stat/words",
            json={
                "stat": [
                    {
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
                    }
                ],
                "fixed": True
            },
            status_code=200
        )

        client = GenericApiClient(timeout=10)
        original_key = settings.api_key
        original_base = settings.api_base_url
        settings.api_key = "test-key"
        settings.api_base_url = "https://mock-api.com"

        try:
            from src.config import endpoints
            import importlib
            importlib.reload(endpoints)

            response = client.fetch_data(
                url=endpoints.endpoints.STATISTIC_WORDS,
                params={"id": "123", "from": "2025-10-01", "to": "2025-10-02"},
                response_model=StatResponse
            )
            assert isinstance(response, StatResponse)
            assert len(response.stat) == 1
        finally:
            settings.api_key = original_key
            settings.api_base_url = original_base
            importlib.reload(endpoints)