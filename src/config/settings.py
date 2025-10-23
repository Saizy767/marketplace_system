from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path

class Settings(BaseSettings):
    api_key: str = Field(..., env="API_KEY")
    api_base_url: str = Field(..., env="API_BASE_URL")

    class Config:
        env_file = Path(__file__).parent.parent.parent / ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()