from airflow.models.baseoperator import BaseOperator
from src.transformers.base import BaseTransformer
from src.schemas.api_schemas.stats_keywords import StatResponse

class TransformOperator(BaseOperator):
    def __init__(self, transformer: BaseTransformer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transformer = transformer

    def execute(self, context):
        ti = context["task_instance"]
        raw_data = ti.xcom_pull(task_ids="fetch_keywords")
        if not raw_data:
            self.log.warning("No data to transform")
            return []

        
        response = StatResponse.model_validate(raw_data)

        records = self.transformer.transform(response, **context)
        self.log.info(f"✅ Transformed {len(records)} records")
        return records