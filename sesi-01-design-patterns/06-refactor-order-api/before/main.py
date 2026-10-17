"""Order API - BEFORE (titik awal hands-on)

Semua ada di satu file dan satu endpoint:
- koneksi DB global, query SQL langsung di route
- aturan diskon pakai if/elif
- pilih channel notifikasi pakai if/elif
- config dibaca langsung dari os.getenv di tengah kode

Tugas: refactor ke folder after/ memakai pattern yang sudah dibahas.
Jalankan: uvicorn main:app --reload
"""
import os
import sqlite3

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

conn = sqlite3.connect(os.getenv("DATABASE_PATH", "orders.db"), check_same_thread=False)
conn.execute(
    "CREATE TABLE IF NOT EXISTS orders ("
    "id INTEGER PRIMARY KEY, customer TEXT, customer_type TEXT, subtotal INTEGER, total INTEGER)"
)

app = FastAPI(title="Order API (before)")


class Item(BaseModel):
    name: str
    price: int = Field(gt=0)
    qty: int = Field(gt=0)


class OrderIn(BaseModel):
    customer: str
    customer_type: str = "regular"
    items: list[Item]


@app.post("/orders", status_code=201)
def create_order(payload: OrderIn):
    subtotal = sum(i.price * i.qty for i in payload.items)

    if payload.customer_type == "regular":
        discount = 0
    elif payload.customer_type == "member":
        discount = subtotal * 5 // 100
    elif payload.customer_type == "vip":
        discount = subtotal * 10 // 100
    else:
        raise HTTPException(400, "Tipe customer tidak dikenal")
    total = subtotal - discount

    cur = conn.execute(
        "INSERT INTO orders (customer, customer_type, subtotal, total) VALUES (?, ?, ?, ?)",
        (payload.customer, payload.customer_type, subtotal, total),
    )
    conn.commit()
    order_id = cur.lastrowid

    channel = os.getenv("NOTIFICATION_CHANNEL", "email")
    if channel == "email":
        print(f"[EMAIL] ke {payload.customer}: Order #{order_id} total Rp{total:,}")
    elif channel == "sms":
        print(f"[SMS] ke {payload.customer}: Order #{order_id} total Rp{total:,}")

    return {"id": order_id, "customer": payload.customer, "subtotal": subtotal, "total": total}


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    row = conn.execute(
        "SELECT id, customer, subtotal, total FROM orders WHERE id = ?", (order_id,)
    ).fetchone()
    if not row:
        raise HTTPException(404, "Order tidak ditemukan")
    return {"id": row[0], "customer": row[1], "subtotal": row[2], "total": row[3]}
