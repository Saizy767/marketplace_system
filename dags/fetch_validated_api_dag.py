from datetime import datetime 
from airflow import DAG
from src.operators.api_fetch import ApiFetchOperator
from src.config.endpoints import endpoints

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
        "advert_id": "29441288",
    },
)

fetch_keywords_task = ApiFetchOperator(
    task_id="fetch_keywords",
    url=endpoints.STATISTIC_WORDS,
    params={
        "advert_id": "{{ params.advert_id }}",
        "from": "{{ data_interval_start | ds }}",
        "to": "{{ data_interval_end | ds }}",
    },
    dag=dag,
)