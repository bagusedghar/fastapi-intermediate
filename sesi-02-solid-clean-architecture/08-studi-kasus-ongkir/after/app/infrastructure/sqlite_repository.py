"""Infrastructure: adapter SQLite untuk port OrderRepository."""
import sqlite3
from dataclasses import replace

from app.domain.order import Order


class SqliteOrderRepository:
    def __init__(self, path: str):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS orders ("
            "id INTEGER PRIMARY KEY, customer TEXT, customer_type TEXT, courier TEXT, "
            "subtotal INTEGER, shipping_cost INTEGER, total INTEGER)"
        )

    def add(self, order: Order) -> Order:
        cur = self.conn.execute(
            "INSERT INTO orders (customer, customer_type, courier, subtotal, shipping_cost, total) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (order.customer, order.customer_type, order.courier, order.subtotal, order.shipping_cost, order.total),
        )
        self.conn.commit()
        return replace(order, id=cur.lastrowid)

    def get(self, order_id: int) -> Order | None:
        row = self.conn.execute(
            "SELECT customer, customer_type, courier, subtotal, shipping_cost, total, id FROM orders WHERE id = ?",
            (order_id,),
        ).fetchone()
        return Order(*row) if row else None
