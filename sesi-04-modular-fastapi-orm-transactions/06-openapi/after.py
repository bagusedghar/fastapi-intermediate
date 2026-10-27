"""OpenAPI - AFTER

Dokumentasi dibuat dari kode, jadi cukup lengkapi metadata-nya:
- judul, versi, dan deskripsi API
- tags untuk mengelompokkan endpoint
- summary di setiap endpoint
- response_model dan responses untuk menjelaskan bentuk sukses dan error
- contoh request lewat Field(examples=...)

Jalankan: uvicorn after:app --reload, lalu buka http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="Order API",
    version="1.0.0",
    description="API untuk membuat dan melihat order.",
    openapi_tags=[{
        "name": "orders",
        "description": "Membuat dan melihat order",
    }],
)
ORDERS: dict[int, dict] = {}


class OrderIn(BaseModel):
    customer: str = Field(examples=["budi@mail.com"])
    product_id: int = Field(gt=0, examples=[1])
    qty: int = Field(gt=0, examples=[2])


class OrderOut(BaseModel):
    id: int
    customer: str
    product_id: int
    qty: int
    status: str


class ErrorOut(BaseModel):
    detail: str


@app.post(
    "/orders", status_code=201, response_model=OrderOut,
    tags=["orders"], summary="Buat order baru",
)
def create_order(payload: OrderIn):
    data = payload.model_dump()
    order = {"id": len(ORDERS) + 1, "status": "pending", **data}
    ORDERS[order["id"]] = order
    return order


@app.get(
    "/orders/{order_id}", response_model=OrderOut,
    tags=["orders"], summary="Lihat detail order",
    responses={404: {"model": ErrorOut,
                     "description": "Order tidak ditemukan"}},
)
def get_order(order_id: int):
    if order_id not in ORDERS:
        raise HTTPException(404, "Order tidak ditemukan")
    return ORDERS[order_id]
