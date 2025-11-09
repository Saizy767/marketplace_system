from airflow.models.baseoperator import BaseOperator
from src.loaders.base import BaseLoader

class LoadToDbOperator(BaseOperator):
    """
    Airflow-оператор для загрузки преобразованных данных в СУБД.
    Извлекает записи из XCom (task_id='transform_keywords') и передаёт их
    в инстанс загрузчика, реализующего BaseLoader.
    """
    def __init__(self, loader: BaseLoader, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loader = loader

    def execute(self, context):
        ti = context["task_instance"]
        records = ti.xcom_pull(task_ids="transform_keywords")
        if not records:
            self.log.warning("No records to load")
            return 0

        loaded = self.loader.load(records, **context)
        self.log.info(f"✅ Loaded {loaded} records into DB")
        return loaded