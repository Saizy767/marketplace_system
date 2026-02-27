from typing import List, Dict, Any
from sqlalchemy.dialects.postgresql import insert
from src.loaders.base import BaseLoader
from src.db.base import BaseEngineManager
from src.tables.orders import Orders
from src.tables.base import Base


class PostgresOrdersLoader(BaseLoader):
    """
    Загрузчик данных в таблицу orders PostgreSQL через ORM-модель Orders.
    Использует ON CONFLICT DO NOTHING по уникальному ключу srid.
    """
    
    def __init__(self, engine_manager: BaseEngineManager):
        self.engine_manager = engine_manager
        engine = self.engine_manager.get_engine()
        Base.metadata.create_all(engine, tables=[Orders.__table__], checkfirst=True)
    
    def load(self, records: List[Dict[str, Any]], **context) -> int:
        if not records:
            return 0
        
        engine = self.engine_manager.get_engine()
        table = Orders.__table__
        CHUNK_SIZE = 1000
        total_loaded = 0
        
        with engine.begin() as conn:
            for i in range(0, len(records), CHUNK_SIZE):
                chunk = records[i:i + CHUNK_SIZE]
                stmt = insert(table).values(chunk)
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=[
                        "date_release",
                        "srid"
                    ])
                result = conn.execute(stmt)
                total_loaded += (result.rowcount if getattr(result, 'rowcount', None) is not None else len(chunk))
        
        return total_loaded