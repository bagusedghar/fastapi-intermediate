"""Pagination - AFTER (keyset / cursor)

Client mengirim id terakhir yang sudah dia lihat, query melanjutkan dari situ:
    WHERE id < :after ORDER BY id DESC LIMIT 20
Database langsung loncat lewat index primary key, jadi halaman jauh sama cepatnya dengan halaman awal.
Order baru tidak membuat data bergeser.

Trade-off: tidak bisa loncat langsung ke halaman tertentu, cuma bisa lanjut ke halaman berikutnya.
Cocok untuk infinite scroll dan API, kurang cocok untuk tabel admin dengan nomor halaman.

Butuh PostgreSQL + data demo: docker compose up -d, lalu python seed_demo.py (dari folder sesi-07)
Jalankan demo: python after.py
"""
import os
import time

from sqlalchemy import create_engine, text

engine = create_engine(os.getenv("DEMO_DATABASE_URL", "postgresql+psycopg://app:app@localhost:5432/demo"))

FIRST_PAGE = text("SELECT id, customer, created_at FROM orders ORDER BY id DESC LIMIT 20")
NEXT_PAGE = text("SELECT id, customer, created_at FROM orders "
                 "WHERE id < :after ORDER BY id DESC LIMIT 20")


def list_orders(conn, after: int | None = None):
    rows = conn.execute(FIRST_PAGE if after is None else NEXT_PAGE, {"after": after}).all()
    next_after = rows[-1].id if len(rows) == 20 else None      # cursor untuk halaman berikutnya
    return rows, next_after


def timed(fn, *args):
    start = time.perf_counter()
    result = fn(*args)
    return (time.perf_counter() - start) * 1000, result


if __name__ == "__main__":
    with engine.connect() as conn:
        list_orders(conn)                                 # pemanasan
        for page, after in ((1, None), (9000, 20021)):    # 20021 = id terakhir di halaman 8999
            ms, (rows, next_after) = timed(list_orders, conn, after)
            print(f"Halaman {page:>4}: {ms:5.1f} ms, id {rows[0].id}..{rows[-1].id}, next_after={next_after}")
