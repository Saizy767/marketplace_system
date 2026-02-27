from unittest import mock
from src.config import endpoints

with mock.patch("airflow.models.Variable.get") as mock_get:
    mock_get.side_effect = lambda key, default=None: {
        "API_KEY": "test-api-key",
        "API_BASE_URL": "https://api.test.com",
    }.get(key, default)
    

def test_endpoints_construction():
    endpoints_module = endpoints.get_endpoints()
    assert endpoints_module.STATISTIC_WORDS.endswith("/adv/v0/normquery/stats")
    assert "API_BASE_URL" not in endpoints_module.STATISTIC_WORDS


def test_other_endpoint_present():
    endpoints_module = endpoints.get_endpoints()
    assert hasattr(endpoints_module, "ACTIVE_ADVERTS")
    assert "/api/advert/v2/adverts" in getattr(endpoints_module, "ACTIVE_ADVERTS")
