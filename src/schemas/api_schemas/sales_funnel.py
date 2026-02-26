from datetime import datetime
from pydantic import BaseModel, Field


class Product(BaseModel):
    nmId: int = Field(..., description="Артикул WB")
    title: str = Field(..., description="Название карточки товара")
    vendorCode: str = Field(..., description="Артикул продавца")
    brandName: str = Field(..., description="Бренд")
    subjectId: int = Field(..., description="ID предмета")
    subjectName: str = Field(..., description="Название предмета")


class History(BaseModel):
    date: datetime = Field(..., description="Дата сбора статистики")
    openCount: int = Field(..., description="Количество переходов в карточку товара")
    cartCount: int = Field(..., description="Положили в корзину, шт.")
    orderCount: int = Field(..., description="Заказали товаров, шт.")
    orderSum: int = Field(..., description="Заказали на сумму")
    buyoutCount: int = Field(..., description="Выкупили товаров, шт.")
    buyoutSum: int = Field(..., description="Выкупили на сумму")
    buyoutPercent: int = Field(..., description="Процент выкупа")
    addToCartConversion: int = Field(..., 
                                     description="""Конверсия в корзину.
                                     Какой процент посетителей, открывших 
                                     карточку товара, добавили товар в 
                                     корзину, %""")
    cartToOrderConversion: int = Field(...,
                                       description="""Конверсия в заказ. 
                                       Какой процент посетителей, добавивших 
                                       товар в корзину, сделали заказ""")
    addToWishlistCount: int = Field(...,
                                    description="""Количество добавлений 
                                    товара в Отложенные""")


class SalesFunnel(BaseModel):
    product: Product = Field(..., description="Карточка товара")
    history: History = Field(..., description="Статистика за период")
    currency: str = Field(..., description="Валюта отчёта")