"""
Юнит-тесты для валидации Pydantic-схем, используемых в API.
"""

from src.schemas.api_schemas.stats_keywords import (
    StatsResponse,
    AdvertStat,
    StatItem,
)
from src.schemas.api_schemas.active_adverts import (
    ActiveAdvertsResponse,
    Advert,
    Settings,
    Placements,
    Timestamps,
    NmSetting,
    BidsKopecks,
    Subject,
)


def test_stats_response_parsing():
    """Статистика ключевых слов корректно валидируется в модель."""
    payload = {
        "stat": [
            {
                "advert_id": 456,
                "nm_id": 789,
                "stats": [
                    {
                        "atbs": 0,
                        "avg_pos": 1.0,
                        "clicks": 10,
                        "cpc": 15.0,
                        "cpm": 0.0,
                        "ctr": 0.1,
                        "norm_query": "телефон",
                        "orders": 0,
                        "shks": 0,
                        "views": 100,
                        "spend": 1500,
                    }
                ],
            }
        ]
    }

    model = StatsResponse.model_validate(payload)
    assert isinstance(model, StatsResponse)
    assert len(model.stat) == 1

    advert_stat = model.stat[0]
    assert isinstance(advert_stat, AdvertStat)
    assert advert_stat.advert_id == 456
    assert advert_stat.nm_id == 789

    inner = advert_stat.stats[0]
    assert isinstance(inner, StatItem)
    assert inner.norm_query == "телефон"
    assert inner.views == 100


def test_active_adverts_response_parsing():
    """Активные объявления и связанные вложенные модели должны валидироваться."""
    payload = {
        "adverts": [
            {
                "id": 1,
                "status": 9,
                "bid_type": "manual",
                "nm_settings": [
                    {
                        "bids_kopecks": {"recommendations": 10, "search": 5},
                        "nm_id": 111,
                        "subject": {"id": 22, "name": "Товар"},
                    }
                ],
                "settings": {
                    "name": "Test Campaign",
                    "payment_type": "daily",
                    "placements": {"search": True, "recommendations": False},
                },
                "timestamps": {
                    "created": "2025-01-01T00:00:00",
                    "deleted": "2025-12-31T23:59:59",
                    "started": None,
                    "updated": "2025-06-01T12:00:00",
                },
            }
        ]
    }

    model = ActiveAdvertsResponse.model_validate(payload)
    assert isinstance(model, ActiveAdvertsResponse)
    assert len(model.adverts) == 1

    advert = model.adverts[0]
    # top‑level advert model
    assert isinstance(advert, Advert)
    assert advert.status == 9
    assert isinstance(advert.settings, Settings)
    assert isinstance(advert.settings.placements, Placements)
    assert isinstance(advert.timestamps, Timestamps)

    # nm_settings list and nested model types
    assert isinstance(advert.nm_settings, list)
    nm_setting = advert.nm_settings[0]
    assert isinstance(nm_setting, NmSetting)
    assert nm_setting.nm_id == 111
    assert isinstance(nm_setting.subject, Subject)
    assert isinstance(nm_setting.bids_kopecks, BidsKopecks)


def test_timestamps_accepts_future_deleted_and_started_none():
    ts = Timestamps(
        created="2025-01-01T00:00:00",
        deleted="2099-01-01T00:00:00",
        started=None,
        updated="2025-06-01T12:00:00",
    )
    assert ts.deleted.year == 2099
    assert ts.started is None


def test_order_schema_date_and_bool_coercion():
    from src.schemas.api_schemas.orders import Order

    payload = {
        "date": {"date": "2025-01-01T10:00:00Z"},
        "lastChangeDate": "2025-01-02T11:00:00",
        "cancelDate": "0001-01-01T00:00:00",
        "warehouseName": "W",
        "warehouseType": "T",
        "countryName": "C",
        "oblastOkrugName": "O",
        "regionName": "R",
        "supplierArticle": "SA",
        "nmId": 123,
        "barcode": "B",
        "category": "Cat",
        "subject": "Sub",
        "techSize": "TS",
        "incomeID": 1,
        "isSupply": True,
        "isRealization": False,
        "totalPrice": 10.0,
        "discountPercent": 5,
        "spp": 1.0,
        "finishedPrice": 8.0,
        "priceWithDisc": 7.0,
        "sticker": "S",
        "gNumber": "G",
        "srid": "SR",
    }
    order = Order.model_validate(payload)
    # вложенная дата корректно разбирается
    assert order.date_release.year == 2025
    # нулевая cancelDate превращается в None
    assert order.cancelDate is None
    # булевы значения приводятся к строкам
    assert order.isSupply == "True"
    assert order.isRealization == "False"

