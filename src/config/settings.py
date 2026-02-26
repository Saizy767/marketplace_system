from pydantic_settings import BaseSettings
from airflow.models import Variable

class Settings(BaseSettings):
    """
    Класс для получения конфигурационных параметров из Airflow Variables.
    """
    @property
    def api_key(self) -> str:
        return Variable.get("API_KEY")

    @property
    def api_base_url(self) -> str:
        return Variable.get("API_BASE_URL")
    
    @property
    def api_statistic_url(self) -> str:
        return Variable.get("API_STATISTIC_URL")
    
    @property
    def api_seller_url(self) -> str:
        return Variable.get("API_SELLER_URL")

    model_config = {"extra": "ignore"}