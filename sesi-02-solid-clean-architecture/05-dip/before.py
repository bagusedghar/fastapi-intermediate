"""DIP (Dependency Inversion) - BEFORE

OrderService membuat sendiri repository dan notifier-nya di __init__.
Artinya OrderService terikat ke SQLite dan email. Mau test tanpa database? Tidak bisa,
karena dari luar kita tidak bisa mengganti apa yang dipakai di dalamnya.
"""
import sqlite3


class SqliteOrderRepository:
    def __init__(self):
        self.conn = sqlite3.connect("orders.db")
        self.conn.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, customer TEXT, total INTEGER)")

    def add(self, customer: str, total: int) -> int:
        cur = self.conn.execute("INSERT INTO orders (customer, total) VALUES (?, ?)", (customer, total))
        self.conn.commit()
        return cur.lastrowid


class EmailNotifier:
    def send(self, to: str, message: str) -> None:
        print(f"[EMAIL] ke {to}: {message}")


class OrderService:
    def __init__(self):
        self.repo = SqliteOrderRepository()  # terikat ke SQLite
        self.notifier = EmailNotifier()      # terikat ke email

    def place_order(self, customer: str, total: int) -> int:
        order_id = self.repo.add(customer, total)
        self.notifier.send(customer, f"Order #{order_id} dibuat")
        return order_id


if __name__ == "__main__":
    OrderService().place_order("budi@mail.com", 150_000)
