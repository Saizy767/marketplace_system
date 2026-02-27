"""
Юнит‑тесты загрузчиков в базу данных. Меняются менеджер/движок на заглушки,
чтобы подсчитать исполненные SQL-вызовы.
"""

from unittest.mock import Mock
import src.tables.base as tables_base
tables_base.Base.metadata.create_all = lambda *a, **k: None

from src.loaders.postgres_keyword_stats import PostgresKeywordStatsLoader
from src.loaders.postgres_sales_funnel import PostgresSalesFunnelLoader
from src.loaders.postgres_orders import PostgresOrdersLoader


class DummyConn:
    def __init__(self):
        self.executed = []
    def execute(self, stmt):
        self.executed.append(stmt)
        class R:
            rowcount = len(self.executed)
        return R()

class DummyEngine:
    def __init__(self):
        self.conn = DummyConn()
    def begin(self):
        class CM:
            def __init__(self, conn):
                self.conn = conn
            def __enter__(self):
                return self.conn
            def __exit__(self, exc_type, exc, tb):
                pass
        return CM(self.conn)

class DummyManager:
    def __init__(self):
        self.engine = DummyEngine()
    def get_engine(self):
        return self.engine


def test_keyword_stats_loader_empty():
    # пустой список не приводит к запросам и возвращает 0
    loader = PostgresKeywordStatsLoader(engine_manager=DummyManager())
    assert loader.load([]) == 0


def test_keyword_stats_loader_basic():
    # базовая загрузка нескольких записей должна выполнить по крайней мере один запрос
    manager = DummyManager()
    loader = PostgresKeywordStatsLoader(engine_manager=manager)
    records = [{"advert_id": 1}, {"advert_id": 2}]
    count = loader.load(records)
    assert count >= 1
    assert len(manager.engine.conn.executed) >= 1


def test_sales_funnel_loader_empty():
    # аналогично: при пустом входе возвращаем 0
    loader = PostgresSalesFunnelLoader(engine_manager=DummyManager())
    assert loader.load([]) == 0


def test_sales_funnel_loader_basic():
    # загрузчик для воронки должен вставить один тестовый объект
    manager = DummyManager()
    loader = PostgresSalesFunnelLoader(engine_manager=manager)
    records = []
    rec = Mock()
    rec.__dict__ = {"nmId": 1}
    records.append(rec)
    count = loader.load(records)
    assert count == 1
    assert len(manager.engine.conn.executed) >= 1


def test_orders_loader_empty():
    # пустой список заказов -> 0
    loader = PostgresOrdersLoader(engine_manager=DummyManager())
    assert loader.load([]) == 0


def test_orders_loader_basic():
    # проверяем, что при списке заказов выполняются SQL-вызовы
    manager = DummyManager()
    loader = PostgresOrdersLoader(engine_manager=manager)
    recs = [{"srid": 1}, {"srid": 2}]
    result = loader.load(recs)
    assert result >= 1
    assert len(manager.engine.conn.executed) >= 1
