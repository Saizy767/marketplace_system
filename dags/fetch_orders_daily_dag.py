from datetime import datetime, date, time as dtime, timedelta, timezone
from typing import List, Dict, Any
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.exceptions import AirflowSkipException
from src.api_client.generic import GenericApiClient
from src.config.endpoints import get_endpoints
from src.schemas.api_schemas.orders import Order, OrdersResponse
from src.transformers.orders import OrdersTransformer
from src.loaders.postgres_orders import PostgresOrdersLoader
from src.db.postgres import PostgresEngineManager


START_DATE = datetime(2026, 2, 2)

default_args = {
    "owner": "saizy",
    "retries": 3,
    "retry_delay": 60,
    "email_on_failure": False,
}

dag = DAG(
    dag_id="fetch_orders_daily",
    default_args=default_args,
    description="Ежедневная загрузка данных по заказам за предыдущий день",
    schedule="0 0 * * *",  # Каждый день в 00:00 UTC
    start_date=START_DATE,
    catchup=False,
    tags=["api", "etl", "orders", "daily"],
)


def fetch_orders(**context) -> List[Dict[str, Any]]:
    """
    Получает заказы за предыдущий день через API.
    Использует интервал: [вчера 00:00, сегодня 00:00)
    """
    ti = context["task_instance"]
    logical_date = context["logical_date"]
    
    start_date = (logical_date - timedelta(days=1)).replace(tzinfo=timezone.utc)
    end_date = logical_date.replace(tzinfo=timezone.utc)
    
    ti.log.info(f"📥 Запрос заказов за период: {start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}")
    
    client = GenericApiClient(timeout=60)
    url = get_endpoints().ORDERS_LIST
    
    try:
        raw_data = client.fetch_data(
            url=url,
            params={
                "dateFrom": start_date.strftime("%Y-%m-%dT00:00:00Z"),
                "flag": 0,
            },
            response_model=OrdersResponse,
        )
        
        orders_count = len(raw_data.orders) if hasattr(raw_data, 'orders') else 0
        ti.log.info(f"✅ Получено {orders_count} заказов за {start_date.strftime('%Y-%m-%d')}")
        
        if not orders_count:
            ti.log.warning("⚠️  Нет заказов за указанный период")
            raise AirflowSkipException("No orders found for the period")
        
        # Сериализуем для передачи через XCom — возвращаем dicts, не JSON-строки
        return [order.model_dump() for order in raw_data.orders]
    
    except Exception as e:
        ti.log.error(f"❌ Ошибка при получении заказов: {str(e)}")
        raise


def transform_orders(**context) -> List[Dict[str, Any]]:
    """Преобразует сырые данные заказов в формат для загрузки в БД"""
    ti = context["task_instance"]
    raw_orders = ti.xcom_pull(task_ids="fetch_orders")
    
    if not raw_orders:
        ti.log.warning("⚠️  Нет данных для трансформации")
        return []
    
    ti.log.info(f"🔄 Трансформация {len(raw_orders)} заказов")
    
    # Валидируем через Pydantic
    orders = [Order.model_validate(order) for order in raw_orders]
    
    # Применяем трансформер
    transformer = OrdersTransformer()
    transformed = transformer.transform(orders, **context)

    # Make XCom-safe: convert date/time objects to ISO strings
    safe = []
    for r in transformed:
        r2 = {}
        for k, v in r.items():
            if isinstance(v, (datetime, date)):
                r2[k] = v.isoformat()
            elif isinstance(v, dtime):
                r2[k] = v.isoformat()
            else:
                r2[k] = v
        safe.append(r2)

    ti.log.info(f"✅ Преобразовано {len(transformed)} записей для загрузки (XCom-safe)")
    return safe


def load_orders_to_db(**context) -> int:
    """Загружает преобразованные заказы в PostgreSQL"""
    ti = context["task_instance"]

    records = ti.xcom_pull(task_ids="transform_orders")

    if not records:
        ti.log.warning("⚠️  Нет записей для загрузки")
        return 0

    ti.log.info(f"💾 Загрузка {len(records)} заказов в БД")

    try:
        # Parse date/time strings back to date/time objects for DB loader
        parsed_records = []
        for r in records:
            r2 = {}
            for k, v in r.items():
                if isinstance(v, str):
                    # date fields in ISO date format 'YYYY-MM-DD' or datetime 'YYYY-MM-DDTHH:MM:SS'
                    try:
                        if k in ("time_release",):
                            r2[k] = dtime.fromisoformat(v)
                        elif k in ("date_release", "lastChangeDate", "cancelDate"):
                            # keep only date part if datetime string provided
                            r2[k] = date.fromisoformat(v.split("T")[0])
                        else:
                            r2[k] = v
                    except Exception:
                        r2[k] = v
                else:
                    r2[k] = v
            parsed_records.append(r2)

        engine_manager = PostgresEngineManager(conn_id="postgres")
        loader = PostgresOrdersLoader(engine_manager=engine_manager)
        loaded_count = loader.load(parsed_records)

        ti.log.info(f"✅ Успешно загружено {loaded_count} заказов в таблицу orders")
        return loaded_count

    except Exception as e:
        ti.log.error(f"❌ Ошибка при загрузке в БД: {str(e)}")
        raise


# Определение задач
fetch_task = PythonOperator(
    task_id="fetch_orders",
    python_callable=fetch_orders,
    dag=dag,
)

transform_task = PythonOperator(
    task_id="transform_orders",
    python_callable=transform_orders,
    dag=dag,
)

load_task = PythonOperator(
    task_id="load_orders_to_db",
    python_callable=load_orders_to_db,
    dag=dag,
)

end_task = EmptyOperator(
    task_id="end",
    dag=dag,
    trigger_rule="none_failed_min_one_success",
)

# Установка зависимостей
fetch_task >> transform_task >> load_task >> end_task