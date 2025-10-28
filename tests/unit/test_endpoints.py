from unittest import mock
from src.config import endpoints

with mock.patch("airflow.models.Variable.get") as mock_get:
    mock_get.side_effect = lambda key, default=None: {
        "API_KEY": "test-api-key",
        "API_BASE_URL": "https://api.test.com",
    }.get(key, default)
    

def test_endpoints_construction():
    endpoints_module = endpoints.get_endpoints()
    assert endpoints_module.STATISTIC_WORDS.endswith("/adv/v1/stat/words")
    assert "API_BASE_URL" not in endpoints_module.STATISTIC_WORDS