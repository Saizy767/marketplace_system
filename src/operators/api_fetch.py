from airflow.models.baseoperator import BaseOperator
from src.api_client.generic import GenericApiClient


class ApiFetchOperator(BaseOperator):
    def __init__(self, url: str, params: dict = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = url
        self.params = params or {}

    def execute(self, context):
        client = GenericApiClient()
        data = client.fetch_data(url=self.url, params=self.params)
        return data