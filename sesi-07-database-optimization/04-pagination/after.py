"""Pagination - AFTER (keyset / cursor)

Client mengirim id terakhir yang sudah dia lihat, query melanjutkan dari situ:
    WHERE id < :after ORDER BY id DESC LIMIT 20
Database langsung loncat lewat index primary key, jadi halaman jauh sama cepatnya dengan halaman awal.
Order baru tidak membuat data bergeser.

Trade-off: tidak bisa loncat langsung ke halaman tertentu, cuma bisa lanjut ke halaman berikutnya.
Cocok untuk infinite scroll dan API, kurang cocok untuk tabel admin dengan nomor halaman.

Butuh PostgreSQL + data dummy: docker compose up -d, lalu python seed_demo.py (dari folder sesi-07)
Jalankan demo: python after.py
"""
import os
import time

from sqlalchemy import create_engine, text

DB_URL = os.getenv("DEMO_DATABASE_URL",
                   "postgresql+psycopg://app:app@localhost:5432/demo")
engine = create_engine(DB_URL)

FIRST_PAGE = text("SELECT id, customer, created_at FROM orders "
                  "ORDER BY id DESC LIMIT 20")
NEXT_PAGE = text("SELECT id, customer, created_at FROM orders "
                 "WHERE id < :after ORDER BY id DESC LIMIT 20")


def list_orders(conn, after: int | None = None):
    query = FIRST_PAGE if after is None else NEXT_PAGE
    rows = conn.execute(query, {"after": after}).all()
    # cursor untuk halaman berikutnya
    next_after = rows[-1].id if len(rows) == 20 else None
    return rows, next_after


def timed(fn, *args):
    start = time.perf_counter()
    result = fn(*args)
    return (time.perf_counter() - start) * 1000, result


if __name__ == "__main__":
    with engine.connect() as conn:
        list_orders(conn)                       # pemanasan
        # 20021 = id terakhir di halaman 8999
        for page, after in ((1, None), (9000, 20021)):
            ms, (rows, next_after) = timed(list_orders, conn, after)
            print(f"Halaman {page:>4}: {ms:5.1f} ms, "
                  f"id {rows[0].id}..{rows[-1].id}, "
                  f"next_after={next_after}")
