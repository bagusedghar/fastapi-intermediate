"""APIRouter - BEFORE

Semua endpoint ditumpuk di main.py: product, order, nanti user, payment, report...
File makin panjang, prefix "/products" dan "/orders" ditulis berulang,
dan dua developer yang mengerjakan fitur berbeda sering bentrok di file yang sama.

Jalankan: uvicorn before:app --reload
"""
from fastapi import FastAPI

app = FastAPI()
PRODUCTS = {1: {"id": 1, "name": "Keyboard", "price": 500_000}}
ORDERS: dict[int, dict] = {}


@app.get("/products")
def list_products():
    return list(PRODUCTS.values())


@app.get("/products/{product_id}")
def get_product(product_id: int):
    return PRODUCTS[product_id]


@app.post("/orders", status_code=201)
def create_order(customer: str):
    order = {"id": len(ORDERS) + 1, "customer": customer}
    ORDERS[order["id"]] = order
    return order


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    return ORDERS[order_id]
