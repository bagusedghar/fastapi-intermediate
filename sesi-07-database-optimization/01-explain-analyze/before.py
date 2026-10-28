"""EXPLAIN ANALYZE - BEFORE

Endpoint riwayat order customer terasa lambat.
Yang kita punya cuma angka waktunya, tanpa tahu APA yang membuatnya lambat.
Tebakan "tambah server saja" atau "pakai cache saja" belum tentu menyelesaikan masalahnya.

Butuh PostgreSQL + data dummy: docker compose up -d, lalu python seed_demo.py (dari folder sesi-07)
Jalankan demo: python before.py
"""
import os
import time

from sqlalchemy import create_engine, text

DB_URL = os.getenv("DEMO_DATABASE_URL",
                   "postgresql+psycopg://app:app@localhost:5432/demo")
engine = create_engine(DB_URL)

HISTORY = text("""
    SELECT id, status, created_at FROM orders
    WHERE customer = :customer
    ORDER BY created_at DESC
    LIMIT 10
""")


def order_history(conn, customer: str) -> list:
    return conn.execute(HISTORY, {"customer": customer}).all()


if __name__ == "__main__":
    with engine.begin() as conn:
        conn.execute(text(               # mulai tanpa index
            "DROP INDEX IF EXISTS ix_orders_customer_created"))

        start = time.perf_counter()
        rows = order_history(conn, "customer42@mail.com")
        ms = (time.perf_counter() - start) * 1000
        print(f"{len(rows)} order, {ms:.1f} ms. "
              "Kita belum mengetahui penyebab lambatnya query.")
