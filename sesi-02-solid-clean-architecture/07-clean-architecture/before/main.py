"""Order API - titik awal Sesi 2 (hasil akhir Sesi 1)

Route hanya menghandle HTTP. Semua komponen dirakit di get_order_service().

Semua file masih sejajar di satu folder dan service masih meng-import discounts secara langsung.
Di Sesi 2 struktur ini dipecah per layer (lihat after/).

Jalankan: uvicorn main:app --reload
"""
from functools import lru_cache

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field

from config import get_settings
from notifiers import create_notifier
from repository import SqliteOrderRepository
from service import OrderNotFound, OrderService

app = FastAPI(title="Order API (after)")


class Item(BaseModel):
    name: str
    price: int = Field(gt=0)
    qty: int = Field(gt=0)


class OrderIn(BaseModel):
    customer: str
    customer_type: str = "regular"
    items: list[Item]


@lru_cache
def get_order_service() -> OrderService:
    settings = get_settings()
    return OrderService(
        repo=SqliteOrderRepository(settings.database_path),
        notifier=create_notifier(settings.notification_channel),
    )


@app.post("/orders", status_code=201)
def create_order(payload: OrderIn, service: OrderService = Depends(get_order_service)):
    try:
        items = [i.model_dump() for i in payload.items]
        return service.place_order(payload.customer, payload.customer_type, items)
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.get("/orders/{order_id}")
def get_order(order_id: int, service: OrderService = Depends(get_order_service)):
    try:
        return service.get_order(order_id)
    except OrderNotFound as e:
        raise HTTPException(404, str(e))
