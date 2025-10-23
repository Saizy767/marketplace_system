from src.config.endpoints import endpoints

def test_endpoints_construction():
    assert endpoints.STATISTIC_WORDS.endswith("/adv/v1/stat/words")
    assert "API_BASE_URL" not in endpoints.STATISTIC_WORDS