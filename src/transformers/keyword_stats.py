from datetime import datetime
from typing import Any, List, Dict
from src.transformers.base import BaseTransformer
from src.schemas.api_schemas.stats_keywords import StatResponse


class KeywordStatsTransformer(BaseTransformer):
    def transform(self, data: Any, **context) -> List[Dict[str, Any]]:
        if not isinstance(data, StatResponse):
            raise TypeError(
                f"Expected StatResponse, got {type(data).__name__}"
            )
        
        advert_id = context.get("advert_id")
        if not advert_id:
            raise ValueError("Missing required context: 'advert_id'")
        
        logical_end = context["data_interval_end"]
        send_time = logical_end.time().replace(second=0, microsecond=0) 

        records = []
        for stat in data.stat:
            stat_date = stat.begin.date()

            if stat.keyword == "Всего по кампании":
                continue

            records.append({
                "advert_id": str(advert_id),
                "date": stat_date,
                "send_time": send_time,
                "keyword": stat.keyword,
                "clicks": stat.clicks,
                "views": stat.views,
                "sum": float(stat.sum),
            })

        return records