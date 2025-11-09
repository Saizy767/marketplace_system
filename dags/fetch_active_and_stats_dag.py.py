from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.exceptions import AirflowSkipException
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from src.operators.fetch_active_adverts import FetchActiveAdvertsOperator

START_DATE = datetime(2025, 10, 1)

default_args = {
    "owner": "saizy",
    "retries": 2,
    "retry_delay": 60,
    "email_on_failure": False,
}

dag = DAG(
    dag_id="fetch_active_adverts_and_stats",
    default_args=default_args,
    description="Fetch active adverts and trigger stats collection for each",
    schedule="@hourly",  # или "@daily", "*/30 * * * *", и т.д.
    start_date=START_DATE,
    catchup=False,
    tags=["api", "etl", "adverts", "keywords", "dynamic"],
)

fetch_active_task = FetchActiveAdvertsOperator(
    task_id="fetch_active_adverts",
    dag=dag,
)

def prepare_conf_for_each_advert(**context):
    ti = context["task_instance"]
    active_ids = ti.xcom_pull(task_ids="fetch_active_adverts")
    if not active_ids:
        raise AirflowSkipException
    return [{"advert_id": str(aid)} for aid in active_ids]

prepare_conf_task = PythonOperator(
    task_id="prepare_dagrun_conf",
    python_callable=prepare_conf_for_each_advert,
    dag=dag,
)

trigger_stats_tasks = TriggerDagRunOperator.partial(
    task_id="trigger_keyword_stats",
    trigger_dag_id="fetch_keywords_from_api",
    dag=dag,
).expand(conf=prepare_conf_task.output)

fetch_active_task >> prepare_conf_task >> trigger_stats_tasks