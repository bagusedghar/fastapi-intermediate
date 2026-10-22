"""Connection Pool - BEFORE

NullPool = tanpa pool. Setiap request membuka koneksi baru ke PostgreSQL lalu menutupnya.
Membuka koneksi itu berat: TCP handshake, autentikasi, dan PostgreSQL membuat proses baru per koneksi.
Saat traffic tinggi, jumlah koneksi bisa melewati max_connections dan request mulai ditolak.

Butuh PostgreSQL + data demo: docker compose up -d, lalu python seed_demo.py (dari folder sesi-07)
Jalankan demo: python before.py
"""
import os
import time
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import create_engine, event, text
from sqlalchemy.pool import NullPool

DATABASE_URL = os.getenv("DEMO_DATABASE_URL", "postgresql+psycopg://app:app@localhost:5432/demo")
engine = create_engine(DATABASE_URL, poolclass=NullPool)
connections_opened = 0


@event.listens_for(engine, "connect")
def count_connection(*args):
    global connections_opened
    connections_opened += 1


def get_order(order_id: int):
    with engine.connect() as conn:                    # buka koneksi baru
        return conn.execute(text("SELECT * FROM orders WHERE id = :id"), {"id": order_id}).one()


if __name__ == "__main__":
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=10) as pool:  # 10 request bersamaan
        list(pool.map(get_order, range(1, 501)))
    print(f"500 request: {(time.perf_counter() - start) * 1000:.0f} ms, koneksi dibuka: {connections_opened}")
