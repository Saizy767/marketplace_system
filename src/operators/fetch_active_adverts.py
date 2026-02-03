from airflow.models import BaseOperator
from src.api_client.generic import GenericApiClient
from src.config.endpoints import get_endpoints
from src.schemas.api_schemas.active_adverts import ActiveAdvertsResponse


class FetchActiveAdvertsOperator(BaseOperator):
    """
    Airflow-оператор для получения списка активных рекламных кампаний из внешнего API.
    Фильтрует кампании по статусу 9 (активные) и возвращает список их adverts.
    Использует GenericApiClient и Pydantic-модель ActiveAdvertsResponse для валидации.
    """    
    def execute(self, context) -> ActiveAdvertsResponse:
        client = GenericApiClient(timeout=30)
        url = get_endpoints().ACTIVE_ADVERTS
        response: ActiveAdvertsResponse = client.fetch_data(
            url=url,
            response_model=ActiveAdvertsResponse,
        )

        active_adverts = [
            advert.model_dump(mode="json")
            for advert in response.adverts 
            if advert.status == 9
        ]
        self.log.info(f"✅ Найдено {len(active_adverts)} активных рекламных компаний: {active_adverts}")
        return active_adverts