import requests_mock
from src.api_client.generic import GenericApiClient
from src.schemas.api_schemas.stats_keywords import KeywordListResponse
from src.config.settings import settings

def test_full_api_call_mocked():
    with requests_mock.Mocker() as m:
        m.get(
            "https://mock-api.com/adv/v1/stat/words",
            json={"keywords": [{"date": "2025-10-14", "stats": []}]},
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
                params={"advert_id": "123", "from": "2025-10-01", "to": "2025-10-02"},
                response_model=KeywordListResponse
            )
            assert isinstance(response, KeywordListResponse)
            assert len(response.keywords) == 1
        finally:
            # Восстанавливаем
            settings.api_key = original_key
            settings.api_base_url = original_base
            importlib.reload(endpoints)