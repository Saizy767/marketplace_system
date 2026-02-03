from airflow.models.baseoperator import BaseOperator
from src.transformers.base import BaseTransformer
from src.schemas.api_schemas.stats_keywords import StatsResponse

class TransformOperator(BaseOperator):
    """
    Airflow-оператор для преобразования сырых данных из XCom в структурированные записи.
    Извлекает данные из задачи 'fetch_keywords', валидирует их через StatsResponse,
    применяет переданный трансформер и возвращает список записей.
    """
    def __init__(self, transformer: BaseTransformer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transformer = transformer

    def execute(self, context):
        ti = context["task_instance"]
        raw_data = ti.xcom_pull(task_ids="fetch_keywords")
        if not raw_data:
            self.log.warning("No data to transform")
            return []

        
        response = StatsResponse.model_validate(raw_data)

        records = self.transformer.transform(response, **context)
        self.log.info(f"✅ Transformed {len(records)} records")
        return records