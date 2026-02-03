from src.config.endpoints import ApiEndpoints
from src.api_client.generic import GenericApiClient
from src.schemas.api_schemas.stats_keywords import StatsResponse
from src.transformers.keyword_stat import KeywordStatsTransformer
from src.loaders.postgres_keyword_stats import PostgresKeywordStatsLoader
from src.db.postgres import PostgresEngineManager
from datetime import datetime, timezone

# === Настройки ===
advert_id = "29441288"
start_date = datetime(2025, 10, 23, 0, 0, 0, tzinfo=timezone.utc)
end_date = datetime(2025, 10, 24, 0, 0, 0, tzinfo=timezone.utc)

endpoints = ApiEndpoints()

print("🔍 1. Fetch: Запрос к API...")
client = GenericApiClient(timeout=30)
try:
    raw_response = client.fetch_data(
        url=endpoints.STATISTIC_WORDS,
        params={
            "id": advert_id,
            "from": start_date,
            "to": end_date,
        },
        response_model=StatsResponse,
    )
    print(f"✅ Получено {len(raw_response.stat)} дней")
except Exception as e:
    print(f"❌ Ошибка при запросе: {e}")
    exit(1)

print("🔄 2. Transform: Преобразование данных...")
transformer = KeywordStatsTransformer()
try:
    records = transformer.transform(raw_response, 
                                    advert_id=advert_id,
                                    data_interval_start=start_date,
                                    data_interval_end=end_date
                                    ) 
    print(f"✅ Преобразовано {len(records)} записей")
except Exception as e:
    print(f"❌ Ошибка при трансформации: {e}")
    exit(1)

print("💾 3. Load: Загрузка в PostgreSQL...")
try:
    engine_manager = PostgresEngineManager(conn_id="postgres")
    loader = PostgresKeywordStatsLoader(engine_manager=engine_manager)
    loaded_count = loader.load(records)
    print(f"✅ Успешно загружено {loaded_count} записей в таблицу public.keyword_stats")
except Exception as e:
    print(f"❌ Ошибка при загрузке в БД: {e}")
    exit(1)

print("🎉 ETL-процесс завершён успешно!")