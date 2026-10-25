"""Repository - AFTER

Semua akses data dibungkus di class repository dengan method add() dan get().
place_order() hanya tahu "simpan order", tidak tahu disimpan di mana.
Ada dua implementasi: SQLite untuk aplikasi, in-memory untuk test.
"""
import sqlite3
from typing import Protocol


class OrderRepository(Protocol):
    def add(self, customer: str, total: int) -> int: ...
    def get(self, order_id: int) -> dict | None: ...


class SqliteOrderRepository:
    def __init__(self, path: str = "orders.db"):
        self.conn = sqlite3.connect(path)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS orders "
            "(id INTEGER PRIMARY KEY, customer TEXT, total INTEGER)"
        )

    def add(self, customer: str, total: int) -> int:
        cur = self.conn.execute(
            "INSERT INTO orders (customer, total) VALUES (?, ?)",
            (customer, total),
        )
        self.conn.commit()
        return cur.lastrowid

    def get(self, order_id: int) -> dict | None:
        row = self.conn.execute(
            "SELECT id, customer, total FROM orders WHERE id = ?", (order_id,)
        ).fetchone()
        return {"id": row[0], "customer": row[1], "total": row[2]} if row else None


class InMemoryOrderRepository:
    def __init__(self):
        self.rows: dict[int, dict] = {}

    def add(self, customer: str, total: int) -> int:
        order_id = len(self.rows) + 1
        self.rows[order_id] = {"id": order_id, "customer": customer, "total": total}
        return order_id

    def get(self, order_id: int) -> dict | None:
        return self.rows.get(order_id)


def place_order(repo: OrderRepository, customer: str, subtotal: int) -> int:
    total = subtotal - subtotal * 5 // 100
    return repo.add(customer, total)


if __name__ == "__main__":
    for repo in (SqliteOrderRepository(), InMemoryOrderRepository()):
        order_id = place_order(repo, "budi@mail.com", 200_000)
        print(type(repo).__name__, repo.get(order_id))
