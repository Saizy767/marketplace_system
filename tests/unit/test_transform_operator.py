from unittest.mock import Mock
from src.operators.transform import TransformOperator
from src.schemas.api_schemas.stats_keywords import StatsResponse


class DummyTransformer:
    def __init__(self):
        self.called = False
    def transform(self, data, **context):
        self.called = True
        return [{"hello": "world"}]


def test_transform_operator_no_data(monkeypatch):
    # XCom возвращает None
    ti = Mock()
    ti.xcom_pull.return_value = None
    op = TransformOperator(task_id="t", transformer=DummyTransformer())
    result = op.execute({"task_instance": ti})
    assert result == []
    ti.xcom_pull.assert_called_with(task_ids="fetch_keywords")


def test_transform_operator_success(monkeypatch):
    raw = {"stat": []}
    ti = Mock()
    ti.xcom_pull.return_value = raw
    transformer = DummyTransformer()
    op = TransformOperator(task_id="t", transformer=transformer)
    res = op.execute({"task_instance": ti})
    assert transformer.called
    assert res == [{"hello": "world"}]
