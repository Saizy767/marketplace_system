from unittest import mock

from src.config.settings import Settings


def test_settings_reads_variables():
    with mock.patch("airflow.models.Variable.get") as mock_get:
        mock_get.side_effect = lambda key, default=None: {
            "API_KEY": "abc",
            "API_BASE_URL": "https://api.x",
            "API_STATISTIC_URL": "https://api.x/stat",
            "API_SELLER_URL": "https://api.x/sell",
        }.get(key, default)
        s = Settings()
        assert s.api_key == "abc"
        assert s.api_base_url == "https://api.x"
        assert s.api_statistic_url == "https://api.x/stat"
        assert s.api_seller_url == "https://api.x/sell"
