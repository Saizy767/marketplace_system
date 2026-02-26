from typing import Any, Dict, List
from src.schemas.api_schemas.sales_funnel import SalesFunnel
from src.transformers.base import BaseTransformer


class SalesFunnelTransformer(BaseTransformer):
    def transform(self, sales_funnel: List[SalesFunnel], **context) -> List[Dict[str, Any]]:
        """Трансформер данных воронки продаж из API в формат для загрузки в БД."""
        if not isinstance(sales_funnel, list):
            raise TypeError(f"Expected list of SalesFunnel, got {type(sales_funnel).__name__}")
        
        ti = context.get("task_instance")
        if ti:
            ti.log.info(f"📊 Обработка {len(sales_funnel)} записей воронки продаж")

        result = []
        for item in sales_funnel:
            if isinstance(item, dict):
                item = SalesFunnel(**item)
            record = {
                "nmId": item.product.nmId,
                "title": item.product.title,
                "vendorCode": item.product.vendorCode,
                "date_release": item.history.date.date() if hasattr(item.history.date, 'date') else item.history.date,
                "openCount": item.history.openCount,
                "cartCount": item.history.cartCount,
                "orderCount": item.history.orderSum,
                "orderSum": item.history.orderSum,
                "buyoutCount": item.history.buyoutCount,
                "buyoutSum": item.history.buyoutSum,
                "buyoutPercent": item.history.buyoutPercent,
                "addToCartConversion": item.history.addToCartConversion,
                "cartToOrderConversion": item.history.cartToOrderConversion,
                "addToWishlistCount": item.history.addToWishlistCount
            }
            result.append(record)
        return result
