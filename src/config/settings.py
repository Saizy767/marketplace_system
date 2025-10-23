from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_key: str = Field(..., validation_alias="API_KEY")
    api_base_url: str = Field(..., validation_alias="API_BASE_URL")


settings = Settings()