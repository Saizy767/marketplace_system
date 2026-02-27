"""
Тесты оператора LoadToDbOperator. Они проверяют поведение с отсутствием
и наличием записей, а также передачу данных загрузчику.
"""

from unittest.mock import Mock

from src.operators.load_to_db import LoadToDbOperator
from src.loaders.base import BaseLoader


class DummyLoader(BaseLoader):
    def __init__(self):
        self.received = None
    def load(self, records, **context):
        self.received = records
        return 42


def test_load_to_db_operator_no_records():
    # если XCom не возвращает данных, оператор должен вернуть 0
    ti = Mock()
    ti.xcom_pull.return_value = None
    op = LoadToDbOperator(task_id="t", loader=DummyLoader())
    result = op.execute({"task_instance": ti})
    assert result == 0
    ti.xcom_pull.assert_called_with(task_ids="transform_keywords")


def test_load_to_db_operator_with_records():
    # при наличии списка записей они передаются в loader и результат
    ti = Mock()
    ti.xcom_pull.return_value = [{"a": 1}]
    loader = DummyLoader()
    op = LoadToDbOperator(task_id="t", loader=loader)
    result = op.execute({"task_instance": ti})
    assert result == 42
    assert loader.received == [{"a": 1}]
