import pendulum
from datetime import (timedelta, time as dt_time)
from typing import Any, List, Dict, Optional
from src.schemas.api_schemas.active_adverts import AdvertNmMapping
from src.transformers.base import BaseTransformer
from src.schemas.api_schemas.stats_keywords import StatsResponse

class KeywordStatsTransformer(BaseTransformer):
    """
    Трансформер данных статистики ключевых слов из API в формат для загрузки в БД.
    - Группирует записи по дате.
    - Агрегирует данные по каждому ключевому слову.
    - Извлекает `adverts` из `dag_run.conf`.
    - Формирует `send_time` как время окончания интервала DAG + 3 часа,
      сохраняя только часы и минуты в формате 'HH:MM'.
    - Возвращает список записей с полями: advert_id, date, send_time, info_keywords (JSONB).
    """
    def transform(self, data: StatsResponse, **context) -> List[Dict[str, Any]]:
        if not isinstance(data, StatsResponse):
            raise TypeError(f"Expected StatsResponse, got {type(data).__name__}")
        
        ti = context.get("task_instance")
        if ti:
            ti.log.info(f"📊 Raw API response structure: {data.model_dump(exclude={'stats': {'__all__': {'stats'}}})}")
            ti.log.info(f"🔢 Total AdvertStat records: {len(data.stats)}")
            
            # Отладка: проверяем содержимое каждого AdvertStat
            for i, advert_stat in enumerate(data.stats):
                ti.log.info(
                    f"📈 AdvertStat #{i}: advert_id={advert_stat.advert_id}, "
                    f"nm_id={advert_stat.nm_id}, stats_count={len(advert_stat.stats)}"
                )
                if not advert_stat.stats:
                    ti.log.warning(f"⚠️  AdvertStat #{i} has EMPTY stats list! This is why records=0.")
        
        
        data_interval_start = context.get("data_interval_start")
        if not data_interval_start:
            raise ValueError("Missing 'data_interval_start' in context")
        
        # Форматируем дату как строку в формате 'YYYY-MM-DD'
        start_date = data_interval_start.strftime("%Y-%m-%d")
        
        dag_run_conf = context.get("dag_run", {}).conf or {}
        adverts: Optional[list[AdvertNmMapping]] = dag_run_conf.get("adverts")

        if not adverts:
            raise ValueError("Missing required context: 'adverts'")

        logical_end = context["data_interval_end"]
        if hasattr(logical_end, 'time'):
            send_time_obj = logical_end.time()
        else:
            send_time_obj = logical_end

        logical_end_plus_3 = logical_end + timedelta(hours=3)

        if isinstance(send_time_obj, (dt_time, pendulum.Time)):
            send_time_str = logical_end_plus_3.strftime("%H:%M:%S")
        else:
            send_time_str = str(logical_end_plus_3)
        
        result = []
        for advert_stat in data.stats:
            for stat in advert_stat.stats:
                result.append({
                    "advert_id": str(advert_stat.advert_id),
                    "nm_id": str(advert_stat.nm_id),
                    "start_date": start_date,
                    "send_time": send_time_str,
                    "atbs": stat.atbs,
                    "avg_pos": stat.avg_pos,
                    "clicks": stat.clicks,
                    "cpc": stat.cpc,
                    "cpm": stat.cpm,
                    "ctr": stat.ctr,
                    "norm_query": stat.norm_query,
                    "orders": stat.orders,
                    "shks": stat.shks,
                    "views": stat.views,
                })

        if not result and ti:
            ti.log.warning("⚠️ No stats found in transformed data")

        return result