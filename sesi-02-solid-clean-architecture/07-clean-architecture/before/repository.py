"""Repository: semua SQL ada di sini. InMemoryOrderRepository dipakai untuk test."""
import sqlite3
from typing import Protocol


class OrderRepository(Protocol):
    def add(self, order: dict) -> dict: ...
    def get(self, order_id: int) -> dict | None: ...


class SqliteOrderRepository:
    def __init__(self, path: str):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS orders ("
            "id INTEGER PRIMARY KEY, customer TEXT, customer_type TEXT, subtotal INTEGER, total INTEGER)"
        )

    def add(self, order: dict) -> dict:
        cur = self.conn.execute(
            "INSERT INTO orders (customer, customer_type, subtotal, total) VALUES (?, ?, ?, ?)",
            (order["customer"], order["customer_type"], order["subtotal"], order["total"]),
        )
        self.conn.commit()
        return {"id": cur.lastrowid, **order}

    def get(self, order_id: int) -> dict | None:
        row = self.conn.execute(
            "SELECT id, customer, customer_type, subtotal, total FROM orders WHERE id = ?", (order_id,)
        ).fetchone()
        if not row:
            return None
        keys = ("id", "customer", "customer_type", "subtotal", "total")
        return dict(zip(keys, row))


class InMemoryOrderRepository:
    def __init__(self):
        self.rows: dict[int, dict] = {}

    def add(self, order: dict) -> dict:
        saved = {"id": len(self.rows) + 1, **order}
        self.rows[saved["id"]] = saved
        return saved

    def get(self, order_id: int) -> dict | None:
        return self.rows.get(order_id)
