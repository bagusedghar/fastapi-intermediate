"""DIP (Dependency Inversion) - AFTER

OrderService bergantung pada interface (Protocol), bukan pada class konkret.
Repository dan notifier dikirim dari luar lewat constructor (dependency injection).
Di aplikasi kita kirim SQLite + email, di test kita kirim versi in-memory.
"""
import sqlite3
from typing import Protocol


class OrderRepository(Protocol):
    def add(self, customer: str, total: int) -> int: ...


class Notifier(Protocol):
    def send(self, to: str, message: str) -> None: ...


class OrderService:
    def __init__(self, repo: OrderRepository, notifier: Notifier):
        self.repo = repo
        self.notifier = notifier

    def place_order(self, customer: str, total: int) -> int:
        order_id = self.repo.add(customer, total)
        self.notifier.send(customer, f"Order #{order_id} dibuat")
        return order_id


# ---------- implementasi untuk aplikasi ----------
class SqliteOrderRepository:
    def __init__(self, path: str = "orders.db"):
        self.conn = sqlite3.connect(path)
        self.conn.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, customer TEXT, total INTEGER)")

    def add(self, customer: str, total: int) -> int:
        cur = self.conn.execute("INSERT INTO orders (customer, total) VALUES (?, ?)", (customer, total))
        self.conn.commit()
        return cur.lastrowid


class EmailNotifier:
    def send(self, to: str, message: str) -> None:
        print(f"[EMAIL] ke {to}: {message}")


# ---------- implementasi untuk test ----------
class InMemoryOrderRepository:
    def __init__(self):
        self.rows: list[tuple[str, int]] = []

    def add(self, customer: str, total: int) -> int:
        self.rows.append((customer, total))
        return len(self.rows)


class FakeNotifier:
    def __init__(self):
        self.sent: list[str] = []

    def send(self, to: str, message: str) -> None:
        self.sent.append(to)


if __name__ == "__main__":
    OrderService(SqliteOrderRepository(), EmailNotifier()).place_order("budi@mail.com", 150_000)

    notifier = FakeNotifier()
    OrderService(InMemoryOrderRepository(), notifier).place_order("budi@mail.com", 150_000)
    print("fake notifier menerima:", notifier.sent)
