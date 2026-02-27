from typing import List, Dict, Any
from sqlalchemy.dialects.postgresql import insert
from src.loaders.base import BaseLoader
from src.db.base import BaseEngineManager
from src.tables.keyword_stat import KeywordStat
from src.tables.base import Base


class PostgresKeywordStatsLoader(BaseLoader):
    """
    Загрузчик данных в таблицу keyword_stats PostgreSQL через ORM-модель KeywordStat.
    Таблица создаётся автоматически при инициализации, если не существует.
    """

    def __init__(self, engine_manager: BaseEngineManager):
        self.engine_manager = engine_manager
        engine = self.engine_manager.get_engine()
        Base.metadata.create_all(engine, tables=[KeywordStat.__table__], checkfirst=True)
    

    def load(self, records: List[Dict[str, Any]], **context) -> int:
        if not records:
            return 0

        engine = self.engine_manager.get_engine()
        table = KeywordStat.__table__


        CHUNK = 1000
        total = 0
        with engine.begin() as conn:
            for i in range(0, len(records), CHUNK):
                chunk = records[i:i+CHUNK]
                stmt = insert(table).values(chunk)
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=["advert_id",
                                    "nm_id",
                                    "start_date",
                                    "send_time",
                                    "norm_query"]
                                    )
                result = conn.execute(stmt)
                total += (result.rowcount if getattr(result, 'rowcount', None) is not None else len(chunk))
        return total