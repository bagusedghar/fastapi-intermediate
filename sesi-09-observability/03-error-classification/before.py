"""Error Classification - BEFORE (semua error diperlakukan sama)

Satu exception handler untuk semua error: status 500 dan log ERROR.
- Kesalahan client (produk tidak ada, stok kurang) ikut tercatat sebagai ERROR
- Tim on-call menerima alert untuk setiap ERROR, termasuk yang bukan masalah server
- Bug sungguhan tidak punya traceback, jadi sulit dicari penyebabnya

Jalankan: python before.py
"""
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

logging.basicConfig(level=logging.INFO,
                    format="%(levelname)-7s %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)   # log client demo
logger = logging.getLogger("orders")
app = FastAPI()

PRODUCTS = {1: {"price": 100_000, "stock": 5},
            3: {"price": 200_000, "stock": 5},
            4: {"price": None, "stock": 5}}  # data rusak, bikin bug


class ProductNotFound(Exception):
    pass


class OutOfStock(Exception):
    pass


class DatabaseUnavailable(Exception):
    pass


@app.post("/products/{product_id}/buy")
def buy(product_id: int, qty: int = 1):
    if product_id == 3:          # anggap: koneksi database timeout
        raise DatabaseUnavailable("koneksi database timeout")
    if product_id not in PRODUCTS:
        raise ProductNotFound(f"produk {product_id} tidak ada")
    product = PRODUCTS[product_id]
    if qty > product["stock"]:
        raise OutOfStock(f"stok produk {product_id} kurang")
    return {"total": product["price"] * qty}


@app.exception_handler(Exception)
async def handle_error(request: Request, exc: Exception):
    logger.error("request gagal: %s", exc)
    return JSONResponse(status_code=500,
                        content={"error": "Internal Server Error"})


if __name__ == "__main__":
    client = TestClient(app, raise_server_exceptions=False)
    for product_id, qty in [(1, 1), (99, 1), (1, 10), (3, 1), (4, 1)]:
        response = client.post(f"/products/{product_id}/buy",
                               params={"qty": qty})
        print(f"  -> produk {product_id} qty {qty}: "
              f"{response.status_code}")
