from src.schemas.api_schemas.stats_keywords import KeywordListResponse

def test_keyword_list_response_valid():
    data = {
        "keywords": [
            {
                "date": "2025-10-14",
                "stats": [
                    {"clicks": 10, 
                     "keyword": "телефон",
                     "sum": 1500.0,
                     "views": 100}
                ]
            }
        ]
    }
    model = KeywordListResponse.model_validate(data)
    assert len(model.keywords) == 1
    assert model.keywords[0].date == "2025-10-14"
    assert model.keywords[0].stats[0].keyword == "телефон"