"""Repository - BEFORE

Hitung total (business logic) dan query SQL (persistence) campur di satu function.
Untuk mengetes perhitungan total saja, kita tetap butuh database.
Kalau nanti pindah ke PostgreSQL atau ORM, function ini juga ikut dibongkar.
"""
import sqlite3

conn = sqlite3.connect("orders.db")
conn.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, customer TEXT, total INTEGER)")


def place_order(customer: str, subtotal: int) -> int:
    total = subtotal - subtotal * 5 // 100  # business logic
    cur = conn.execute(                       # persistence
        "INSERT INTO orders (customer, total) VALUES (?, ?)", (customer, total)
    )
    conn.commit()
    return cur.lastrowid


def get_order(order_id: int):
    row = conn.execute("SELECT id, customer, total FROM orders WHERE id = ?", (order_id,)).fetchone()
    return {"id": row[0], "customer": row[1], "total": row[2]} if row else None


if __name__ == "__main__":
    order_id = place_order("budi@mail.com", 200_000)
    print(get_order(order_id))
