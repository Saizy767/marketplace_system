import pytest
from datetime import datetime, timedelta, timezone
from src.transformers.keyword_stat import KeywordStatsTransformer
from src.schemas.api_schemas.stats_keywords import StatsResponse, AdvertStat, StatItem
from src.schemas.api_schemas.active_adverts import AdvertNmMapping


def make_stats_response():
    # соберём простую структуру с одним advert и двумя stat items
    item1 = StatItem(
        atbs=0, avg_pos=1.0, clicks=1, cpc=2.0, cpm=3.0, ctr=0.1,
        norm_query="q1", orders=0, shks=0, views=10, spend=100
    )
    advert = AdvertStat(advert_id=1, nm_id=2, stats=[item1])
    return StatsResponse(stat=[advert])


def test_transform_success(monkeypatch):
    data = make_stats_response()
    transformer = KeywordStatsTransformer()
    start = datetime(2025, 1, 1, 0, 0, 0)
    end = start + timedelta(hours=1)
    dag_run = {"conf": {"adverts": [{"advert_id": 1, "nm_id": 2}]}}

    result = transformer.transform(
        data,
        data_interval_start=start,
        data_interval_end=end,
        dag_run=dag_run,
    )

    assert isinstance(result, list)
    assert len(result) == 1
    row = result[0]
    assert row["advert_id"] == "1"
    assert row["nm_id"] == "2"
    assert row["start_date"] == "2025-01-01"
    assert "send_time" in row


def test_transform_wrong_type():
    transformer = KeywordStatsTransformer()
    with pytest.raises(TypeError):
        transformer.transform({})


def test_transform_missing_adverts_context():
    transformer = KeywordStatsTransformer()
    data = make_stats_response()
    with pytest.raises(ValueError, match="Missing required context: 'adverts'"):
        transformer.transform(
            data,
            data_interval_start=datetime.now(timezone.utc),
            data_interval_end=datetime.now(timezone.utc),
            dag_run={"conf": {}},
        )


def test_transform_missing_interval_start():
    transformer = KeywordStatsTransformer()
    data = make_stats_response()
    with pytest.raises(ValueError, match="Missing 'data_interval_start'"):
        transformer.transform(
            data,
            data_interval_end=datetime.now(timezone.utc),
            dag_run={"conf": {"adverts": [1]}},
        )


def test_transform_dag_run_object_and_non_datetime_end():
    # DagRun provided as object with conf attr
    class DummyDagRun:
        def __init__(self, conf):
            self.conf = conf
    transformer = KeywordStatsTransformer()
    data = make_stats_response()
    start = datetime(2025, 1, 1)
    logical_end = DummyDagRun(datetime(2025, 1, 1, 5, 0, 0))
    # we'll provide logical_end not used since transform expects data_interval_end directly
    # we bypass by crafting context where logical_end is custom that supports +
    class DummyEnd:
        def __init__(self, dt):
            self.dt = dt
        def __add__(self, td):
            return self.dt + td
        def __str__(self):
            return "dummy"
    end = DummyEnd(datetime(2025, 1, 1, 12, 0, 0))
    dag_run = DummyDagRun({"adverts": [AdvertNmMapping(advert_id=1, nm_id=2)]})
    result = transformer.transform(
        data,
        data_interval_start=start,
        data_interval_end=end,
        dag_run=dag_run,
    )
    assert result  # no exception, send_time from str()


def test_transform_empty_stats_logs_warning():
    transformer = KeywordStatsTransformer()
    # create response with empty stats
    empty_ad = AdvertStat(advert_id=5, nm_id=6, stats=[])
    data = StatsResponse(stat=[empty_ad])
    class DummyLog:
        def __init__(self):
            self.records = []
        def info(self, msg):
            self.records.append(("info", msg))
        def warning(self, msg):
            self.records.append(("warning", msg))
    class DummyTI:
        def __init__(self):
            self.log = DummyLog()
    ti = DummyTI()
    start = datetime(2025, 1, 1)
    end = datetime(2025, 1, 1, 2)
    dag_run = {"conf": {"adverts": [AdvertNmMapping(advert_id=5, nm_id=6)]}}
    res = transformer.transform(
        data,
        task_instance=ti,
        data_interval_start=start,
        data_interval_end=end,
        dag_run=dag_run,
    )
    assert res == []
    # expect at least one warning about EMPTY stats
    assert any("EMPTY stats" in msg for lvl,msg in ti.log.records if lvl=="warning")
