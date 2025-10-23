from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from src.api_client.generic import GenericApiClient
from src.config.endpoints import endpoints
from src.schemas.api_schemas.stats_keywords import KeywordListResponse

def fetch_and_process(**context):
    client = GenericApiClient(timeout=1)
    response = client.fetch_data(
        url=endpoints.STATISTIC_WORDS,
        params={
            'advert_id': '29441288',
            'from': '2025-10-14',
            'to': '2025-10-18'
        },
        response_model=KeywordListResponse,
    )
    return response.model_dump()

default_args = {
    "owner": "saizy",
    "retries": 2,
    "retry_delay": timedelta(minutes=1),
    "email_on_failure": False,
}

# ✅ ЯВНОЕ присваивание DAG переменной на уровне модуля
dag = DAG(
    dag_id="fetch_keywords_from_api",
    default_args=default_args,
    description="Fetch keywords data from external API using GenericApiClient",
    schedule="@hourly",
    start_date=datetime.now() - timedelta(days=1),
    catchup=False,
    tags=["api", "etl", "keywords", "stats"],
)

# Задача, явно привязанная к DAG
fetch_keywords_task = PythonOperator(
    task_id="fetch_keywords",
    python_callable=fetch_and_process,
    dag=dag,
)