from datetime import datetime 
from airflow import DAG
from airflow.operators.python import PythonOperator
from src.transformers.keyword_stats import KeywordStatsTransformer
from src.loaders.postgres_keyword_stats import PostgresKeywordStatsLoader
from src.operators.transform import TransformOperator
from src.operators.load_to_db import LoadToDbOperator
from src.db.postgres import PostgresEngineManager
from src.config.endpoints import get_endpoints
from airflow.exceptions import AirflowFailException
from src.api_client.generic import GenericApiClient
from src.schemas.api_schemas.stats_keywords import StatResponse


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
    schedule="*/5 * * * *", #"@hourly",
    start_date=START_DATE,
    catchup=False,
    tags=["api", "etl", "keywords", "stats"]
)

# === 1. Extract ===
def _fetch_keywords_callable(**context):

    dag_run_conf = context.get("dag_run", {}).conf or {}
    advert_id = dag_run_conf.get("advert_id")
    if not advert_id:
        raise AirflowFailException("❌ 'advert_id' отсутствует")

    params = {
        "id": str(advert_id).strip(),
        "from": context["data_interval_start"].strftime("%Y-%m-%d"),
        "to": context["data_interval_end"].strftime("%Y-%m-%d"),
    }

    client = GenericApiClient()
    data = client.fetch_data(
        url=get_endpoints().STATISTIC_WORDS,
        params=params,
        response_model=StatResponse,
    )
    return data.model_dump(mode="json")

# === 1. Extract ===
fetch_keywords_task = PythonOperator(
    task_id="fetch_keywords",
    python_callable=_fetch_keywords_callable,
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