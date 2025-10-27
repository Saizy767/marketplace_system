from pydantic_settings import BaseSettings
from pydantic import Field
from airflow.models import Variable

class Settings(BaseSettings):
    api_key: str = Variable.get("API_KEY")
    api_base_url: str = Variable.get("API_BASE_URL")
    model_config = {"extra": "ignore"}