import sys
import pytest
from unittest import mock



mock_variable = mock.MagicMock()
mock_variable.get.side_effect = lambda key, default=None: {
    "API_KEY": "test-api-key",
    "API_BASE_URL": "https://api.test.com",
}.get(key, default)


with mock.patch.dict(sys.modules, {"airflow.models": mock.MagicMock(Variable=mock_variable)}):
    pass


@pytest.fixture(autouse=True, scope="session")
def mock_airflow_variables():
    with mock.patch("airflow.models.Variable.get") as mock_get:
        mock_get.side_effect = lambda key, default=None: {
            "API_KEY": "test-api-key",
            "API_BASE_URL": "https://api.test.com",
        }.get(key, default)
        yield