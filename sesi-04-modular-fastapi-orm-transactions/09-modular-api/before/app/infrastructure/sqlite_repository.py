"""Infrastructure: adapter SQLite untuk port OrderRepository.

Bentuk tabel (orders + order_lines) berbeda dengan bentuk domain (Order berisi OrderLine).
Repository yang menerjemahkan keduanya, jadi domain tidak perlu tahu soal tabel.
"""
import sqlite3

from app.domain.money import Money
from app.domain.order import Order, OrderLine, OrderStatus


class SqliteOrderRepository:
    def __init__(self, path: str):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.executescript(
            "CREATE TABLE IF NOT EXISTS orders ("
            " id INTEGER PRIMARY KEY, customer TEXT, customer_type TEXT, status TEXT, discount INTEGER);"
            "CREATE TABLE IF NOT EXISTS order_lines ("
            " order_id INTEGER, product TEXT, price INTEGER, qty INTEGER);"
        )

    def add(self, order: Order) -> Order:
        cur = self.conn.execute(
            "INSERT INTO orders (customer, customer_type, status, discount) VALUES (?, ?, ?, ?)",
            (order.customer, order.customer_type, order.status.value, order.discount.amount),
        )
        order.id = cur.lastrowid
        self.conn.executemany(
            "INSERT INTO order_lines (order_id, product, price, qty) VALUES (?, ?, ?, ?)",
            [(order.id, line.product, line.price.amount, line.qty) for line in order.lines],
        )
        self.conn.commit()
        return order

    def get(self, order_id: int) -> Order | None:
        row = self.conn.execute(
            "SELECT customer, customer_type, status, discount FROM orders WHERE id = ?", (order_id,)
        ).fetchone()
        if row is None:
            return None
        lines = [
            OrderLine(product, Money(price), qty)
            for product, price, qty in self.conn.execute(
                "SELECT product, price, qty FROM order_lines WHERE order_id = ?", (order_id,)
            )
        ]
        customer, customer_type, status, discount = row
        return Order(customer, customer_type, id=order_id, status=OrderStatus(status),
                     lines=lines, discount=Money(discount))

    def save(self, order: Order) -> None:
        # setelah dibuat, yang bisa berubah dari order cuma status-nya
        self.conn.execute("UPDATE orders SET status = ? WHERE id = ?", (order.status.value, order.id))
        self.conn.commit()
