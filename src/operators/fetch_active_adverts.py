from airflow.models import BaseOperator
from src.api_client.generic import GenericApiClient
from src.config.endpoints import get_endpoints
from src.schemas.api_schemas.active_adverts import ActiveAdvertsResponse


class FetchActiveAdvertsOperator(BaseOperator):
    """
    Airflow-оператор для получения списка активных рекламных кампаний из внешнего API.
    Фильтрует кампании по статусу 9 (активные) и возвращает список их advert_id.
    Использует GenericApiClient и Pydantic-модель ActiveAdvertsResponse для валидации.
    """
    def execute(self, context):
        client = GenericApiClient(timeout=30)
        url = get_endpoints().ACTIVE_ADVERTS

        response: ActiveAdvertsResponse = client.fetch_data(
            url=url,
            response_model=ActiveAdvertsResponse,
        )

        active_ids = [advert.id for advert in response.adverts if advert.status == 9]

        self.log.info(f"✅ Найдено {len(active_ids)} активных рекламных компаний: {active_ids}")
        return active_ids