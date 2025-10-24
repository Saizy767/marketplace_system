from typing import List, Dict, Any
from sqlalchemy import (
    Table,
    MetaData, 
    Column, 
    Integer, 
    String, 
    Float, 
    Date,
    Time
    )
from sqlalchemy.dialects.postgresql import insert
from src.loaders.base import BaseLoader
from src.db.base import BaseEngineManager


class PostgresKeywordStatsLoader(BaseLoader):
    def __init__(self, engine_manager: BaseEngineManager, table_name: str = "keyword_stats"):
        self.engine_manager = engine_manager
        self.table_name = table_name

    def _get_table(self, metadata: MetaData):
        return Table(
            self.table_name,
            metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("advert_id", String, nullable=False),
            Column("date", Date, nullable=False),
            Column("send_time", Time, nullable=False),
            Column("keyword", String, nullable=False),
            Column("clicks", Integer, nullable=False),
            Column("views", Integer, nullable=False),
            Column("sum", Float, nullable=False),
            schema=None,
            extend_existing=True,
        )

    def load(self, records: List[Dict[str, Any]], **context) -> int:
        if not records:
            return 0

        engine = self.engine_manager.get_engine()
        metadata = MetaData()
        table = self._get_table(metadata)

        table.create(engine, checkfirst=True)

        with engine.begin() as conn:
            stmt = insert(table).values(records)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=["advert_id", "date", "send_time", "keyword"]
            )
            result = conn.execute(stmt)
            return result.rowcount