from typing import List, Dict, Any
from src.transformers.base import BaseTransformer
from src.schemas.api_schemas.orders import Order


class OrdersTransformer(BaseTransformer):
    """
    Трансформер данных заказов из API в формат для загрузки в БД.
    Конвертирует поля из ответа API в соответствие с моделью таблицы orders.
    """
    
    def transform(self, orders: List[Order], **context) -> List[Dict[str, Any]]:
        if not isinstance(orders, list):
            raise TypeError(f"Expected list of Order, got {type(orders).__name__}")
        
        ti = context.get("task_instance")
        if ti:
            ti.log.info(f"📊 Обработка {len(orders)} заказов")
        
        result = []
        for order in orders:
            if isinstance(order, dict):
                order = Order(**order)
            # Конвертация дат/времён из datetime в date/time для совместимости с моделью БД
            dr = order.date_release
            if hasattr(dr, "time") and hasattr(dr, "date"):
                date_release_val = dr.date()
                time_release_val = dr.time()
            else:
                date_release_val = dr
                time_release_val = None

            lcd = order.lastChangeDate
            last_change_date_val = lcd.date() if hasattr(lcd, 'date') else lcd
            record = {
                "date_release": date_release_val,
                "time_release": time_release_val,
                "lastChangeDate": last_change_date_val,
                "warehouseName": order.warehouseName,
                "warehouseType": order.warehouseType,
                "countryName": order.countryName,
                "oblastOkrugName": order.oblastOkrugName,
                "regionName": order.regionName,
                "supplierArticle": order.supplierArticle,
                "nmId": order.nmId,
                "barcode": order.barcode,
                "category": order.category,
                "subject": order.subject,
                "techSize": order.techSize,
                "incomeID": order.incomeID,
                "isSupply": order.isSupply,
                "isRealization": order.isRealization,
                "totalPrice": order.totalPrice,
                "discountPercent": order.discountPercent,
                "spp": order.spp,
                "finishedPrice": order.finishedPrice,
                "priceWithDisc": order.priceWithDisc,
                "cancelDate": order.cancelDate.date() if hasattr(order.cancelDate, 'date') else order.cancelDate,
                "sticker": order.sticker,
                "gNumber": order.gNumber,
                "srid": order.srid,
            }
            result.append(record)
        
        return result