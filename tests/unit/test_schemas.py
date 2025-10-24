from src.schemas.api_schemas.stats_keywords import StatResponse
import datetime

def test_keyword_list_response_valid():
    data = {
        "stat": [
            {
                "begin": "2025-10-14T00:00:00",
                "end": "2025-10-14T23:59:59",
                "keyword": "телефон",
                "campaignName": "Тестовая кампания",
                "advertId": 29441288,
                "views": 100,
                "clicks": 10,
                "ctr": 0.1,
                "cpc": 15.0,
                "duration": 86400,
                "sum": 1500.0,
                "frq": 1.0
            }
        ]
    }
    model = StatResponse.model_validate(data)
    assert len(model.stat) == 1
    assert model.stat[0].begin.date() == datetime.date(2025, 10, 14)
    assert model.stat[0].keyword == "телефон"