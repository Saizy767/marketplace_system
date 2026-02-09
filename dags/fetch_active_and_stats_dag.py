from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass
import random
import time
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.exceptions import AirflowSkipException
from src.operators.fetch_active_adverts import FetchActiveAdvertsOperator
from src.transformers.keyword_stat import KeywordStatsTransformer
from src.loaders.postgres_keyword_stats import PostgresKeywordStatsLoader
from src.db.postgres import PostgresEngineManager
from src.config.endpoints import get_endpoints
from src.api_client.generic import GenericApiClient
from src.schemas.api_schemas.stats_keywords import StatsResponse
from src.schemas.api_schemas.active_adverts import Advert, AdvertNmMapping

@dataclass
class DagRunContext:
    conf: Dict[str, Any]

START_DATE = datetime(2026, 2, 2)

default_args = {
    "owner": "saizy",
    "retries": 3,
    "retry_delay": 60,
    "email_on_failure": False,
}

dag = DAG(
    dag_id="fetch_active_adverts_and_stats_combined",
    default_args=default_args,
    description="Fetch active adverts and collect stats in one DAG",
    schedule="@hourly",
    start_date=START_DATE,
    catchup=False,
    tags=["api", "etl", "adverts", "keywords", "dynamic"],
)

# 1. Получаем активные объявления
fetch_active_task = FetchActiveAdvertsOperator(
    task_id="fetch_active_adverts",
    dag=dag,
)

# 2. Проверяем есть ли активные объявления
def check_active_adverts(**context) -> str:
    ti = context["task_instance"]
    adverts = ti.xcom_pull(task_ids="fetch_active_adverts")

    if not adverts or not isinstance(adverts, list) or len(adverts) == 0:
        return "no_active_adverts"
    return "prepare_adverts"

check_adverts_task = BranchPythonOperator(
    task_id="check_active_adverts",
    python_callable=check_active_adverts,
    dag=dag,
)

no_active_adverts_task = EmptyOperator(task_id="no_active_adverts", dag=dag)
end_task = EmptyOperator(task_id="end", dag=dag, trigger_rule="none_failed")

# 3. Подготавливаем ID для динамического отображения
def prepare_adverts(**context) -> list[list[AdvertNmMapping]]:
    ti = context["task_instance"]
    adverts = ti.xcom_pull(task_ids="fetch_active_adverts")

    if not adverts:
        raise AirflowSkipException("No active adverts found")
    
    context["task_instance"].log.info(f"Preparing {len(adverts)} active adverts for processing: {adverts}")
    
    validated_adverts: List[Advert] = [
        Advert.model_validate(advert_dict) 
        for advert_dict in adverts
    ]

    # Возвращаем список словарей для динамического отображения
    active_nm: List[AdvertNmMapping] = []

    for advert in validated_adverts:
        if advert.status == 9:
            for advert_setting in advert.nm_settings:
                active_nm.append(
                    {
                        "advert_id": advert.id,
                        "nm_id": advert_setting.nm_id
                    }
                )

    max_advert_session = 10
    sessions = []
    total_batches = (len(active_nm) + max_advert_session - 1) // max_advert_session
    
    for i in range(0, len(active_nm), max_advert_session):
        batch_idx = i // max_advert_session
        is_last_batch = (batch_idx == total_batches - 1)
        
        sessions.append({
            "adverts": active_nm[i : i + max_advert_session],
            "has_next": not is_last_batch
        })
    return sessions

prepare_adverts_task = PythonOperator(
    task_id="prepare_adverts",
    python_callable=prepare_adverts,
    dag=dag,
)

# 4. Полный ETL процесс для одного adverts
def execute_full_etl(adverts: list[AdvertNmMapping], has_next: bool = False, 
                     rate_limit_seconds: float = 6, jitter_seconds: float = 0.1, **context):
    """
    Выполняет полный ETL процесс для одного adverts с использованием существующих компонентов
    """
    ti = context["task_instance"]
    ti.log.info(f"🚀 Starting FULL ETL process for {len(adverts)} adverts (has_next={has_next})")

    if has_next:
        jitter = random.uniform(0, jitter_seconds)
        sleep_for = rate_limit_seconds + jitter
        ti.log.info(f"⏳ Sleeping {sleep_for:.2f}s before next batch to respect API rate limits")
        time.sleep(sleep_for)

    try:
        # === 1. Extract ===
        ti.log.info(f"🔍 Fetching keywords data for {len(adverts)} adverts")
        params = {
            "from": context["data_interval_start"].strftime("%Y-%m-%d"),
            "to": context["data_interval_end"].strftime("%Y-%m-%d"),
            "items": adverts
        }
        ti.log.info(f"FOUND DATA:\n{params}")
        
        client = GenericApiClient(timeout=30)
        raw_data = client.post_data(
            url=get_endpoints().STATISTIC_WORDS,
            json=params,
            response_model=StatsResponse,
        )
        ti.log.info(f"✅ Successfully fetched data for {len(adverts)} adverts, find {len(raw_data.stats)} records")

        # === 2. Transform ===
        ti.log.info(f"🔄 Transforming data for {len(adverts)} adverts")
        transformer = KeywordStatsTransformer()
        
        # Создаем контекст, который ожидает трансформер
        dag_run_conf = {"adverts": adverts}
        task_context = {
            **context,
            "dag_run": DagRunContext(conf=dag_run_conf)
        }
        
        transformed_data = transformer.transform(raw_data, **task_context)
        ti.log.info(f"✅ Successfully transformed {len(transformed_data)} records for {len(adverts)} adverts")
        
        # === 3. Load ===
        ti.log.info(f"💾 Loading data to database for {len(adverts)} adverts")
        engine_manager = PostgresEngineManager(conn_id="postgres")
        loader = PostgresKeywordStatsLoader(engine_manager=engine_manager)
        
        loaded_count = loader.load(transformed_data)
        ti.log.info(f"✅ Successfully loaded {loaded_count} records for {len(adverts)} adverts into keyword_stats table")
        
        return {
            "advert_id": adverts,
            "records_loaded": loaded_count,
            "status": "success"
        }
        
    except Exception as e:
        ti.log.error(f"❌ ETL process FAILED for {len(adverts)} adverts : {str(e)}")
        raise

# 5. Динамически создаем задачи ETL для каждого advert_id
etl_tasks = PythonOperator.partial(
    task_id="execute_etl_for_advert",
    python_callable=execute_full_etl,
    dag=dag,
).expand(op_kwargs=prepare_adverts_task.output)

# Устанавливаем зависимости между задачами
fetch_active_task >> check_adverts_task
check_adverts_task >> [no_active_adverts_task, prepare_adverts_task]
no_active_adverts_task >> end_task
prepare_adverts_task >> etl_tasks >> end_task