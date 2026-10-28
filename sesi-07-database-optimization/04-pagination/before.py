"""Pagination - BEFORE (OFFSET)

LIMIT 20 OFFSET 179980 artinya: baca 180.000 baris, buang 179.980, kembalikan 20.
Halaman awal cepat, halaman jauh makin lambat.
Selain itu, kalau ada order baru masuk saat user pindah halaman, datanya bergeser:
ada order yang tampil dua kali atau terlewat.

Butuh PostgreSQL + data dummy: docker compose up -d, lalu python seed_demo.py (dari folder sesi-07)
Jalankan demo: python before.py
"""
import os
import time

from sqlalchemy import create_engine, text

DB_URL = os.getenv("DEMO_DATABASE_URL",
                   "postgresql+psycopg://app:app@localhost:5432/demo")
engine = create_engine(DB_URL)

PAGE = text("SELECT id, customer, created_at FROM orders "
            "ORDER BY id DESC LIMIT 20 OFFSET :offset")


def list_orders(conn, page: int) -> list:
    return conn.execute(PAGE, {"offset": (page - 1) * 20}).all()


def timed(fn, *args):
    start = time.perf_counter()
    result = fn(*args)
    return (time.perf_counter() - start) * 1000, result


if __name__ == "__main__":
    with engine.connect() as conn:
        list_orders(conn, 1)                    # pemanasan
        for page in (1, 9000):
            ms, rows = timed(list_orders, conn, page)
            print(f"Halaman {page:>4}: {ms:5.1f} ms, "
                  f"id {rows[0].id}..{rows[-1].id}")
