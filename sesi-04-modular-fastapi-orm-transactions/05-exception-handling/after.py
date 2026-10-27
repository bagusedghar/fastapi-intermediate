"""Exception Handling - AFTER

Error dari business logic punya satu class dasar (AppError) dengan code dan status_code.
Satu exception handler mengubah SEMUA AppError jadi format yang sama:
    {"error": {"code": "...", "message": "..."}}
Route tidak perlu try/except lagi, cukup biarkan error-nya naik.

Jalankan: uvicorn after:app --reload
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()
PRODUCTS = {1: {"id": 1, "name": "Keyboard", "stock": 1}}


class AppError(Exception):
    code = "app_error"
    status_code = 400

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ProductNotFound(AppError):
    code = "product_not_found"
    status_code = 404


class OutOfStock(AppError):
    code = "out_of_stock"
    status_code = 409


@app.exception_handler(AppError)
async def handle_app_error(request: Request, exc: AppError):
    body = {"error": {"code": exc.code, "message": exc.message}}
    return JSONResponse(body, status_code=exc.status_code)


def find_product(product_id: int) -> dict:
    if product_id not in PRODUCTS:
        raise ProductNotFound(
            f"Product #{product_id} tidak ditemukan"
        )
    return PRODUCTS[product_id]


@app.get("/products/{product_id}")
def get_product(product_id: int):
    return find_product(product_id)


@app.post("/orders", status_code=201)
def create_order(product_id: int, qty: int):
    product = find_product(product_id)
    if qty > product["stock"]:
        name, stock = product["name"], product["stock"]
        raise OutOfStock(f"Stok {name} tinggal {stock}")
    product["stock"] -= qty
    return {"product_id": product_id, "qty": qty}
