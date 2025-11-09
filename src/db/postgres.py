from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from airflow.providers.postgres.hooks.postgres import PostgresHook
from src.db.base import BaseEngineManager

class PostgresEngineManager(BaseEngineManager):
    """
    Реализация менеджера подключений к PostgreSQL через Airflow Connection.
    """
    def __init__(self, conn_id: str = "postgres_default"):
        self.conn_id = conn_id
        self._engine: Engine | None = None

    def get_engine(self) -> Engine:
        if self._engine is None:
            hook = PostgresHook(postgres_conn_id=self.conn_id)
            self._engine = create_engine(hook.get_uri())
        return self._engine