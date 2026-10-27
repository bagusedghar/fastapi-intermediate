"""OpenAPI - BEFORE

Dokumentasi di /docs dibuat otomatis, tapi seadanya:
- judul "FastAPI", versi 0.1.0, tanpa deskripsi
- nama endpoint hasil tebakan ("Create Order Orders Post")
- bentuk response kosong, error 404 tidak terdokumentasi
Tim frontend harus bertanya dulu ke backend sebelum bisa memakai API.

Jalankan: uvicorn before:app --reload, lalu buka http://127.0.0.1:8000/docs
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
ORDERS: dict[int, dict] = {}


class OrderIn(BaseModel):
    customer: str
    product_id: int
    qty: int


@app.post("/orders", status_code=201)
def create_order(payload: OrderIn):
    data = payload.model_dump()
    order = {"id": len(ORDERS) + 1, "status": "pending", **data}
    ORDERS[order["id"]] = order
    return order


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    if order_id not in ORDERS:
        raise HTTPException(404, "Order tidak ditemukan")
    return ORDERS[order_id]
