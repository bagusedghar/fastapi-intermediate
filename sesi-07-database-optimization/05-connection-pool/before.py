"""Connection Pool - BEFORE

NullPool = tanpa pool. Setiap request membuka koneksi baru ke PostgreSQL lalu menutupnya.
Membuka koneksi itu berat: TCP handshake, autentikasi, dan PostgreSQL membuat proses baru per koneksi.
Saat traffic tinggi, jumlah koneksi bisa melewati max_connections dan request mulai ditolak.

Butuh PostgreSQL + data dummy: docker compose up -d, lalu python seed_demo.py (dari folder sesi-07)
Jalankan demo: python before.py
"""
import os
import time
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import create_engine, event, text
from sqlalchemy.pool import NullPool

DB_URL = os.getenv("DEMO_DATABASE_URL",
                   "postgresql+psycopg://app:app@localhost:5432/demo")
engine = create_engine(DB_URL, poolclass=NullPool)
connections_opened = 0

GET_ORDER = text("SELECT * FROM orders WHERE id = :id")


@event.listens_for(engine, "connect")
def count_connection(*args):
    global connections_opened
    connections_opened += 1


def get_order(order_id: int):
    with engine.connect() as conn:          # buka koneksi baru
        return conn.execute(GET_ORDER, {"id": order_id}).one()


if __name__ == "__main__":
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=10) as pool:  # 10 bersamaan
        list(pool.map(get_order, range(1, 501)))
    ms = (time.perf_counter() - start) * 1000
    print(f"500 request: {ms:.0f} ms, "
          f"koneksi dibuka: {connections_opened}")
