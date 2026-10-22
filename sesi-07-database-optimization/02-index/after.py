"""Index - AFTER

Index = daftar terurut (B-tree) yang menunjuk ke baris di tabel, seperti indeks di belakang buku.
Index (customer, created_at DESC) sesuai dengan query-nya:
- WHERE customer = ...       -> langsung loncat ke order milik customer itu
- ORDER BY created_at DESC   -> datanya sudah urut di index, tidak perlu Sort
- LIMIT 10                   -> berhenti setelah 10 baris

Harganya: index makan storage, dan setiap INSERT/UPDATE ikut memperbarui index.
Jadi buat index untuk query yang memang sering dipakai, bukan untuk semua kolom.

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


def summary(plan: list[str]) -> list[str]:
    """Ambil baris penting saja: jenis scan dan total waktu."""
    return [line.strip() for line in plan if "Scan" in line or "Execution Time" in line]


if __name__ == "__main__":
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_orders_customer_created
            ON orders (customer, created_at DESC)
        """))

        plan = explain(conn, HISTORY, {"customer": "customer42@mail.com"})
        for line in summary(plan):
            print(line)
