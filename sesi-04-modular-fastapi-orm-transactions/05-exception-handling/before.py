"""Exception Handling - BEFORE

Setiap route menangkap error sendiri-sendiri dengan try/except.
Hasilnya format error tidak konsisten:
- GET /products/99     -> {"detail": "Product not found"}
- POST /orders         -> {"msg": "stok habis", "ok": false}
Client (frontend/mobile) jadi harus menangani banyak bentuk error.

Jalankan: uvicorn before:app --reload
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()
PRODUCTS = {1: {"id": 1, "name": "Keyboard", "stock": 1}}


class ProductNotFound(Exception):
    pass


class OutOfStock(Exception):
    pass


def find_product(product_id: int) -> dict:
    if product_id not in PRODUCTS:
        raise ProductNotFound()
    return PRODUCTS[product_id]


@app.get("/products/{product_id}")
def get_product(product_id: int):
    try:
        return find_product(product_id)
    except ProductNotFound:
        raise HTTPException(404, "Product not found")


@app.post("/orders", status_code=201)
def create_order(product_id: int, qty: int):
    try:
        product = find_product(product_id)
        if qty > product["stock"]:
            raise OutOfStock()
        product["stock"] -= qty
        return {"product_id": product_id, "qty": qty}
    except ProductNotFound:
        raise HTTPException(404, "produk tidak ada")
    except OutOfStock:
        body = {"msg": "stok habis", "ok": False}
        return JSONResponse(body, status_code=400)
