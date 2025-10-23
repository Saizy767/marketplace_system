from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.utils.log.logging_mixin import LoggingMixin
from src.api_client.generic import GenericApiClient
from src.config.endpoints import endpoints
from src.schemas.api_schemas.stats_keywords import KeywordListResponse
import logging
import time

def fetch_and_process(**context):
    logger = logging.getLogger("airflow.task")

    logger.info(f"DAG run ID: {context['dag_run'].run_id}")
    logger.info(f"Execution (logical) date: {context['logical_date']}")
    logger.info(f"Task try number: {context['task_instance'].try_number}")

    params = {
        'advert_id': '29441288',
        'from': '2025-10-14',
        'to': '2025-10-18'
    }

    logger.info("Starting keyword data fetch")
    logger.info(f"Parameters: {params}")

    client = GenericApiClient(timeout=30)
    start_time = time.time()

    try:
        response = client.fetch_data(
            url=endpoints.STATISTIC_WORDS,
            params=params,
            response_model=KeywordListResponse,
        )
        duration = time.time() - start_time
        logger.info(f"Fetched {len(response.keywords)} keyword records in {duration:.2f} seconds")
        return response.model_dump()

    except RuntimeError as e:
        logger.error(f"Failed to fetch or validate data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during fetch: {e}")
        raise

default_args = {
    "owner": "saizy",
    "retries": 2,
    "retry_delay": timedelta(minutes=1),
    "email_on_failure": False,
}

dag = DAG(
    dag_id="fetch_keywords_from_api",
    default_args=default_args,
    description="Fetch keywords data from external API using GenericApiClient",
    schedule="@hourly",
    start_date=datetime.now() - timedelta(days=1),
    catchup=False,
    tags=["api", "etl", "keywords", "stats"],
)

fetch_keywords_task = PythonOperator(
    task_id="fetch_keywords",
    python_callable=fetch_and_process,
    dag=dag,
)