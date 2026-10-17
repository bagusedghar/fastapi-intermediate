"""Service Layer - BEFORE

Endpoint FastAPI mengerjakan semuanya: validasi, hitung total,
simpan data, kirim notifikasi. Business logic "terkunci" di dalam HTTP handler,
jadi tidak bisa dipakai ulang (misal dari CLI atau background job)
dan hanya bisa dites lewat request HTTP.

Jalankan: uvicorn before:app --reload
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
ORDERS: dict[int, dict] = {}


class OrderIn(BaseModel):
    customer: str
    subtotal: int


@app.post("/orders", status_code=201)
def create_order(payload: OrderIn):
    if payload.subtotal < 10_000:
        raise HTTPException(400, "Minimal order Rp10.000")
    total = payload.subtotal - payload.subtotal * 5 // 100
    order = {"id": len(ORDERS) + 1, "customer": payload.customer, "total": total}
    ORDERS[order["id"]] = order
    print(f"[EMAIL] ke {payload.customer}: Order #{order['id']} berhasil dibuat")
    return order
