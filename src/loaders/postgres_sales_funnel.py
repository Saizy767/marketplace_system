from typing import Any, Dict, List
from src.db.base import BaseEngineManager
from src.loaders.base import BaseLoader
from src.schemas.api_schemas.sales_funnel import SalesFunnel
from src.tables.base import Base
from sqlalchemy.dialects.postgresql import insert


class PostgresSalesFunnelLoader(BaseLoader):
    """
    Загрузчик данных в таблицу sales_funnel PostgreSQL через ORM-модель SalesFunnel.
    Использует ON CONFLICT DO NOTHING по уникальному ключу (nmId, date_release).
    """
    
    def __init__(self, engine_manager: BaseEngineManager):
        self.engine_manager = engine_manager
        engine = self.engine_manager.get_engine()
        Base.metadata.create_all(engine, tables=[SalesFunnel.__table__], checkfirst=True)
    
    def load(self, records: List[Dict[str, Any]], **context) -> int:
        if not records:
            return 0
        
        engine = self.engine_manager.get_engine()
        table = SalesFunnel.__table__
        CHUNK_SIZE = 1000
        total_loaded = 0
        
        with engine.begin() as conn:
            for i in range(0, len(records), CHUNK_SIZE):
                chunk = records[i:i + CHUNK_SIZE]
                stmt = insert(table).values([record.__dict__ for record in chunk])
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=[
                        "nmId",
                        "date_release"
                    ])
                result = conn.execute(stmt)
                total_loaded += (result.rowcount or 0)
        
        return total_loaded