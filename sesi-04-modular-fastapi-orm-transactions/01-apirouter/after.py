"""APIRouter - AFTER

Endpoint dikelompokkan per fitur dengan APIRouter.
Setiap router punya prefix dan tags sendiri, lalu dipasang ke app dengan include_router().
Di project sungguhan, setiap router ada di file sendiri
(lihat 09-modular-api/after/app/api/routers/). Di sini digabung supaya mudah dibaca.

Jalankan: uvicorn after:app --reload
"""
from fastapi import APIRouter, FastAPI

PRODUCTS = {1: {"id": 1, "name": "Keyboard", "price": 500_000}}
ORDERS: dict[int, dict] = {}

# ---------- api/routers/products.py ----------
products_router = APIRouter(prefix="/products", tags=["products"])


@products_router.get("")
def list_products():
    return list(PRODUCTS.values())


@products_router.get("/{product_id}")
def get_product(product_id: int):
    return PRODUCTS[product_id]


# ---------- api/routers/orders.py ----------
orders_router = APIRouter(prefix="/orders", tags=["orders"])


@orders_router.post("", status_code=201)
def create_order(customer: str):
    order = {"id": len(ORDERS) + 1, "customer": customer}
    ORDERS[order["id"]] = order
    return order


@orders_router.get("/{order_id}")
def get_order(order_id: int):
    return ORDERS[order_id]


# ---------- main.py ----------
app = FastAPI()
app.include_router(products_router)
app.include_router(orders_router)
