from pydantic_settings import BaseSettings
from airflow.models import Variable

class Settings(BaseSettings):
    @property
    def api_key(self) -> str:
        return Variable.get("API_KEY")

    @property
    def api_base_url(self) -> str:
        return Variable.get("API_BASE_URL")

    model_config = {"extra": "ignore"}