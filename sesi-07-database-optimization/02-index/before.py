"""Index - BEFORE

Tabel orders cuma punya index di primary key (id).
Mencari order milik satu customer = membaca 200.000 baris untuk mendapat 40 baris (Seq Scan),
lalu mengurutkan hasilnya. Makin banyak order, makin lambat.

Butuh PostgreSQL + data dummy: docker compose up -d, lalu python seed_demo.py (dari folder sesi-07)
Jalankan demo: python before.py
"""
import os

from sqlalchemy import create_engine, text

DB_URL = os.getenv("DEMO_DATABASE_URL",
                   "postgresql+psycopg://app:app@localhost:5432/demo")
engine = create_engine(DB_URL)

HISTORY = """
    SELECT id, status, created_at FROM orders
    WHERE customer = :customer
    ORDER BY created_at DESC
    LIMIT 10
"""


def explain(conn, sql: str, params: dict) -> list[str]:
    plan = conn.execute(text("EXPLAIN ANALYZE " + sql), params)
    return plan.scalars().all()


def summary(plan: list[str]) -> list[str]:
    """Ambil baris penting saja: jenis scan dan total waktu."""
    return [line.strip() for line in plan
            if "Scan" in line or "Execution Time" in line]


if __name__ == "__main__":
    with engine.begin() as conn:
        conn.execute(text(               # tanpa index
            "DROP INDEX IF EXISTS ix_orders_customer_created"))

        params = {"customer": "customer42@mail.com"}
        for line in summary(explain(conn, HISTORY, params)):
            print(line)
