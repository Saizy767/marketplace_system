import pendulum
from datetime import (timedelta,
                      time as dt_time)
from typing import Any, List, Dict
from src.transformers.base import BaseTransformer
from src.schemas.api_schemas.stats_keywords import StatResponse

class KeywordStatsTransformer(BaseTransformer):
    def transform(self, data: Any, **context) -> List[Dict[str, Any]]:
        if not isinstance(data, StatResponse):
            raise TypeError(f"Expected StatResponse, got {type(data).__name__}")

        dag_run_conf = context.get("dag_run", {}).conf or {}
        advert_id = dag_run_conf.get("advert_id")
        if not advert_id:
            raise ValueError("Missing required context: 'advert_id'")

        logical_end = context["data_interval_end"]
        if hasattr(logical_end, 'time'):
            send_time_obj = logical_end.time()
        else:
            send_time_obj = logical_end

        logical_end_plus_3 = logical_end + timedelta(hours=3)

        if isinstance(send_time_obj, (dt_time, pendulum.Time)):
            send_time_str = logical_end_plus_3.strftime("%H:%M")
        else:
            send_time_str = str(logical_end_plus_3)

        records_by_date = {}

        for stat in data.stat:
            if stat.keyword == "Всего по кампании":
                continue

            stat_date = stat.begin.date()

            if stat_date not in records_by_date:
                records_by_date[stat_date] = {}

            records_by_date[stat_date][stat.keyword] = {
                "clicks": stat.clicks,
                "views": stat.views,
                "sum": float(stat.sum),
            }

        
        result = []
        for date, keywords_dict in records_by_date.items():
            result.append({
                "advert_id": str(advert_id),
                "date": date,
                "send_time": send_time_str,
                "info_keywords": keywords_dict,
            })

        return result