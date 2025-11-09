from typing import List, Dict, Any
from sqlalchemy.dialects.postgresql import insert
from src.loaders.base import BaseLoader
from src.db.base import BaseEngineManager
from src.models.keyword_stat import KeywordStat, Base


class PostgresKeywordStatsLoader(BaseLoader):
    """
    Загрузчик данных в таблицу keyword_stats PostgreSQL через ORM-модель KeywordStat.
    Таблица создаётся автоматически при инициализации, если не существует.
    """

    def __init__(self, engine_manager: BaseEngineManager, table_name: str = "keyword_stats"):
        self.engine_manager = engine_manager
        engine = self.engine_manager.get_engine()
        Base.metadata.create_all(engine, tables=[KeywordStat.__table__], checkfirst=True)
    

    def load(self, records: List[Dict[str, Any]], **context) -> int:
        if not records:
            return 0

        engine = self.engine_manager.get_engine()
        table = KeywordStat.__table__

        with engine.begin() as conn:
            stmt = insert(table).values(records)
            stmt = stmt.on_conflict_do_nothing(
                index_elements=["advert_id", "date", "send_time"]
            )
            result = conn.execute(stmt)
            return result.rowcount