"""Dependency Injection di FastAPI - BEFORE

Service dibuat sekali di level module dan langsung dipakai di route.
Test API mau tidak mau ikut menulis ke orders.db yang asli,
karena tidak ada cara rapi untuk mengganti repository-nya.

Jalankan: uvicorn before:app --reload
"""
import sqlite3

from fastapi import FastAPI
from pydantic import BaseModel


class SqliteOrderRepository:
    def __init__(self, path: str):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS orders "
            "(id INTEGER PRIMARY KEY, customer TEXT, total INTEGER)"
        )

    def add(self, customer: str, total: int) -> dict:
        cur = self.conn.execute(
            "INSERT INTO orders (customer, total) VALUES (?, ?)",
            (customer, total),
        )
        self.conn.commit()
        return {"id": cur.lastrowid, "customer": customer, "total": total}


class OrderService:
    def __init__(self, repo):
        self.repo = repo

    def place_order(self, customer: str, subtotal: int) -> dict:
        return self.repo.add(customer, subtotal - subtotal * 5 // 100)


app = FastAPI()
# dibuat global saat file di-import, susah diganti
service = OrderService(SqliteOrderRepository("orders.db"))


class OrderIn(BaseModel):
    customer: str
    subtotal: int


@app.post("/orders", status_code=201)
def create_order(payload: OrderIn):
    return service.place_order(payload.customer, payload.subtotal)
