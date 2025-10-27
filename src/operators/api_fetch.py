from airflow.models import BaseOperator
from src.api_client.generic import GenericApiClient
from src.schemas.api_schemas.stats_keywords import StatResponse
import time

class ApiFetchOperator(BaseOperator):
    template_fields = ("url", "params")

    def __init__(
        self,
        url: str,
        params: dict = None,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.url = url
        self.params = params or {}

    def execute(self, context):
        self.log.info(f"Starting API fetch from URL: {self.url}")
        self.log.info(f"Using params: {self.params}")

        client = GenericApiClient(timeout=30)
        start_time = time.time()
        try:
            data = client.fetch_data(
                url=self.url,
                params=self.params,
                response_model=StatResponse,
            )
            duration = time.time() - start_time
            keyword_count = len(data.stat)
            self.log.info(
                f"✅ Successfully fetched and validated {keyword_count} keyword records "
                f"in {duration:.2f} seconds"
            )
            return data.model_dump()
        except Exception as e:
            self.log.error(f"❌ Failed to fetch or validate data: {e}")
            raise