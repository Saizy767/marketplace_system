from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.exceptions import AirflowSkipException
from airflow.utils.task_group import TaskGroup
from src.operators.fetch_active_adverts import FetchActiveAdvertsOperator
from src.transformers.keyword_stats import KeywordStatsTransformer
from src.loaders.postgres_keyword_stats import PostgresKeywordStatsLoader
from src.db.postgres import PostgresEngineManager
from src.config.endpoints import get_endpoints
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
def check_active_adverts(**context):
    ti = context["task_instance"]
    active_ids = ti.xcom_pull(task_ids="fetch_active_adverts")
    
    if not active_ids or not isinstance(active_ids, list) or len(active_ids) == 0:
        return "no_active_adverts"
    return "prepare_advert_ids"

check_adverts_task = BranchPythonOperator(
    task_id="check_active_adverts",
    python_callable=check_active_adverts,
    dag=dag,
)

no_active_adverts_task = EmptyOperator(task_id="no_active_adverts", dag=dag)
end_task = EmptyOperator(task_id="end", dag=dag, trigger_rule="none_failed")

# 3. Подготавливаем ID для динамического отображения
def prepare_advert_ids(**context):
    ti = context["task_instance"]
    active_ids = ti.xcom_pull(task_ids="fetch_active_adverts")
    
    if not active_ids:
        raise AirflowSkipException("No active adverts found")
    
    context["task_instance"].log.info(f"Preparing {len(active_ids)} active adverts for processing: {active_ids}")
    
    # Возвращаем список словарей для динамического отображения
    return [{"advert_id": str(aid)} for aid in active_ids]

prepare_advert_ids_task = PythonOperator(
    task_id="prepare_advert_ids",
    python_callable=prepare_advert_ids,
    dag=dag,
)

# 4. Полный ETL процесс для одного advert_id
def execute_full_etl(advert_id, **context):
    """
    Выполняет полный ETL процесс для одного advert_id с использованием существующих компонентов
    """
    ti = context["task_instance"]
    ti.log.info(f"🚀 Starting FULL ETL process for advert_id: {advert_id}")
    
    try:
        # === 1. Extract ===
        ti.log.info(f"🔍 Fetching keywords data for advert_id: {advert_id}")
        params = {
            "id": str(advert_id).strip(),
            "from": context["data_interval_start"].strftime("%Y-%m-%d"),
            "to": context["data_interval_end"].strftime("%Y-%m-%d"),
        }
        ti.log.info(f"FOUND DATA:\n{params}")
        
        client = GenericApiClient(timeout=30)
        raw_data = client.fetch_data(
            url=get_endpoints().STATISTIC_WORDS,
            params=params,
            response_model=StatResponse,
        )
        ti.log.info(f"✅ Successfully fetched data for advert_id: {advert_id}, found {len(raw_data.stat)} records")

        # === 2. Transform ===
        ti.log.info(f"🔄 Transforming data for advert_id: {advert_id}")
        transformer = KeywordStatsTransformer()
        
        # Создаем контекст, который ожидает трансформер
        dag_run_conf = {"advert_id": advert_id}
        task_context = {
            **context,
            "dag_run": type('obj', (object,), {'conf': dag_run_conf})
        }
        
        transformed_data = transformer.transform(raw_data, **task_context)
        ti.log.info(f"✅ Successfully transformed {len(transformed_data)} records for advert_id: {advert_id}")
        
        # === 3. Load ===
        ti.log.info(f"💾 Loading data to database for advert_id: {advert_id}")
        engine_manager = PostgresEngineManager(conn_id="postgres")
        loader = PostgresKeywordStatsLoader(engine_manager=engine_manager)
        
        loaded_count = loader.load(transformed_data)
        ti.log.info(f"✅ Successfully loaded {loaded_count} records for advert_id: {advert_id} into keyword_stats table")
        
        return {
            "advert_id": advert_id,
            "records_loaded": loaded_count,
            "status": "success"
        }
        
    except Exception as e:
        ti.log.error(f"❌ ETL process FAILED for advert_id {advert_id}: {str(e)}")
        raise

# 5. Динамически создаем задачи ETL для каждого advert_id
etl_tasks = PythonOperator.partial(
    task_id="execute_etl_for_advert",
    python_callable=execute_full_etl,
    dag=dag,
).expand(op_kwargs=prepare_advert_ids_task.output)

# Устанавливаем зависимости между задачами
fetch_active_task >> check_adverts_task
check_adverts_task >> [no_active_adverts_task, prepare_advert_ids_task]
no_active_adverts_task >> end_task
prepare_advert_ids_task >> etl_tasks >> end_task