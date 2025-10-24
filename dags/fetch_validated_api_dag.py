from datetime import datetime 
from airflow import DAG
from src.operators.api_fetch import ApiFetchOperator
from src.config.endpoints import endpoints
from src.transformers.keyword_stats import KeywordStatsTransformer
from src.loaders.postgres_keyword_stats import PostgresKeywordStatsLoader
from src.operators.transform import TransformOperator
from src.operators.load_to_db import LoadToDbOperator
from src.db.postgres import PostgresEngineManager


START_DATE = datetime(2025, 10, 1)

default_args = {
    "owner": "saizy",
    "retries": 3,
    "retry_delay": 60,
    "email_on_failure": False,
}

dag = DAG(
    dag_id="fetch_keywords_from_api",
    default_args=default_args,
    description="Fetch keywords data from external API using GenericApiClient",
    schedule="@hourly",
    start_date=START_DATE,
    catchup=True,
    tags=["api", "etl", "keywords", "stats"],
    params={
        "id": "29441288",
    },
)

# === 1. Extract ===
fetch_keywords_task = ApiFetchOperator(
    task_id="fetch_keywords",
    url=endpoints.STATISTIC_WORDS,
    params={
        "id": "{{ params.advert_id }}",
        "from": "{{ data_interval_start | ds }}",
        "to": "{{ data_interval_end | ds }}",
    },
    dag=dag,
)

# === 2. Transform ===
transform_task = TransformOperator(
    task_id="transform_keywords",
    transformer=KeywordStatsTransformer(),
    dag=dag,
)

# === 3. Load ===
engine_manager = PostgresEngineManager(conn_id="postgres")
loader = PostgresKeywordStatsLoader(engine_manager=engine_manager)

load_task = LoadToDbOperator(
    task_id="postgres",
    loader=loader,
    dag=dag,
)

fetch_keywords_task >> transform_task >> load_task