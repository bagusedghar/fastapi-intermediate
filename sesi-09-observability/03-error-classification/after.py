"""Error Classification - AFTER (error dikelompokkan)

Setiap error masuk salah satu dari tiga kelompok:
- client     : kesalahan request (404, 409). Log WARNING, tidak memicu alert
- dependency : layanan lain sedang gangguan (503). Log ERROR, biasanya pulih sendiri, boleh di-retry
- bug        : error yang tidak terduga (500). Log ERROR + traceback supaya penyebabnya bisa dicari
Field error_type di log dipakai untuk filter dan aturan alert.

Jalankan: python after.py
"""
import logging
import traceback

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient


class ShortTraceback(logging.Formatter):
    """Demo: traceback dipendekkan jadi baris kode terakhir saja."""
    def formatException(self, exc_info) -> str:
        frame = traceback.extract_tb(exc_info[2])[-1]
        return (f"  {exc_info[0].__name__}: {exc_info[1]}\n"
                f"  di {frame.name}(), baris {frame.lineno}: "
                f"{frame.line}")


handler = logging.StreamHandler()
handler.setFormatter(ShortTraceback(
    "%(levelname)-7s %(message)s [error_type=%(error_type)s]"))
logging.basicConfig(level=logging.INFO, handlers=[handler])
logging.getLogger("httpx").setLevel(logging.WARNING)   # log client demo
logger = logging.getLogger("orders")
app = FastAPI()

PRODUCTS = {1: {"price": 100_000, "stock": 5},
            3: {"price": 200_000, "stock": 5},
            4: {"price": None, "stock": 5}}  # data rusak, bikin bug


class ClientError(Exception):        # kesalahan dari sisi request
    status_code = 400


class ProductNotFound(ClientError):
    status_code = 404


class OutOfStock(ClientError):
    status_code = 409


class DependencyError(Exception):    # layanan lain sedang gangguan
    status_code = 503


class DatabaseUnavailable(DependencyError):
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


@app.exception_handler(ClientError)
async def handle_client_error(request: Request, exc: ClientError):
    logger.warning("request ditolak: %s", exc,
                   extra={"error_type": "client"})
    return JSONResponse(status_code=exc.status_code,
                        content={"error": str(exc)})


@app.exception_handler(DependencyError)
async def handle_dependency_error(request: Request,
                                  exc: DependencyError):
    logger.error("dependency gangguan: %s", exc,
                 extra={"error_type": "dependency"})
    return JSONResponse(status_code=503,
                        content={"error": "Coba lagi beberapa saat"})


@app.exception_handler(Exception)
async def handle_bug(request: Request, exc: Exception):
    logger.error("error tidak terduga", exc_info=exc,
                 extra={"error_type": "bug"})
    return JSONResponse(status_code=500,
                        content={"error": "Internal Server Error"})


if __name__ == "__main__":
    client = TestClient(app, raise_server_exceptions=False)
    for product_id, qty in [(1, 1), (99, 1), (1, 10), (3, 1), (4, 1)]:
        response = client.post(f"/products/{product_id}/buy",
                               params={"qty": qty})
        print(f"  -> produk {product_id} qty {qty}: "
              f"{response.status_code}")
