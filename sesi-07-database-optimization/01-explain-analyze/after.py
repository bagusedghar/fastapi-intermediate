"""EXPLAIN ANALYZE - AFTER

EXPLAIN ANALYZE menjalankan query lalu menampilkan execution plan-nya:
langkah apa saja yang dilakukan database, berapa baris yang dibaca, dan berapa lama.

Cara membaca (dari baris paling dalam ke atas):
- Seq Scan            : membaca SELURUH tabel, baris demi baris
- Rows Removed by Filter : baris yang dibaca lalu dibuang karena tidak cocok
- actual time / rows  : waktu (ms) dan jumlah baris yang benar-benar dihasilkan
- Execution Time      : total waktu query di database

Butuh PostgreSQL + data demo: docker compose up -d, lalu python seed_demo.py (dari folder sesi-07)
Jalankan demo: python after.py
"""
import os

from sqlalchemy import create_engine, text

engine = create_engine(os.getenv("DEMO_DATABASE_URL", "postgresql+psycopg://app:app@localhost:5432/demo"))

HISTORY = """
    SELECT id, status, created_at FROM orders
    WHERE customer = :customer
    ORDER BY created_at DESC
    LIMIT 10
"""


def explain(conn, sql: str, params: dict) -> list[str]:
    return conn.execute(text("EXPLAIN ANALYZE " + sql), params).scalars().all()


if __name__ == "__main__":
    with engine.begin() as conn:
        conn.execute(text("DROP INDEX IF EXISTS ix_orders_customer_created"))   # mulai tanpa index

        for line in explain(conn, HISTORY, {"customer": "customer42@mail.com"}):
            print(line)
