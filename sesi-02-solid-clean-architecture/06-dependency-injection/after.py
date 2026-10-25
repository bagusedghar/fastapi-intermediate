"""Dependency Injection di FastAPI - AFTER

Repository dan service disediakan lewat function dependency.
Route meminta service dengan Depends(), FastAPI yang merakitnya untuk setiap request.
Di test, get_repository bisa diganti lewat app.dependency_overrides (lihat test_after.py).

Jalankan: uvicorn after:app --reload
"""
import sqlite3
from functools import lru_cache

from fastapi import Depends, FastAPI
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


# ---------- dependency ----------
@lru_cache
def get_repository() -> SqliteOrderRepository:
    return SqliteOrderRepository("orders.db")


def get_order_service(repo=Depends(get_repository)) -> OrderService:
    return OrderService(repo)


# ---------- route ----------
app = FastAPI()


class OrderIn(BaseModel):
    customer: str
    subtotal: int


@app.post("/orders", status_code=201)
def create_order(payload: OrderIn, service: OrderService = Depends(get_order_service)):
    return service.place_order(payload.customer, payload.subtotal)
