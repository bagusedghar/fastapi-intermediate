"""Connection Pool - AFTER

Engine SQLAlchemy menyimpan koneksi yang sudah terbuka dan memakainya ulang (QueuePool, default).
Request selesai = koneksi dikembalikan ke pool, bukan ditutup.

- pool_size      : jumlah koneksi yang disimpan
- max_overflow   : koneksi tambahan saat sibuk, ditutup lagi setelah dipakai
- pool_timeout   : berapa detik menunggu koneksi kosong sebelum error
- pool_pre_ping  : cek koneksi masih hidup sebelum dipakai (misalnya setelah database restart)
- pool_recycle   : ganti koneksi yang sudah terlalu lama terbuka

Batas total koneksi ke database = (pool_size + max_overflow) x jumlah proses aplikasi.
Pastikan masih di bawah max_connections PostgreSQL (default 100).

Butuh PostgreSQL + data demo: docker compose up -d, lalu python seed_demo.py (dari folder sesi-07)
Jalankan demo: python after.py
"""
import os
import time
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import create_engine, event, text

DATABASE_URL = os.getenv("DEMO_DATABASE_URL", "postgresql+psycopg://app:app@localhost:5432/demo")
engine = create_engine(DATABASE_URL,
                       pool_size=10, max_overflow=5,
                       pool_timeout=30,
                       pool_pre_ping=True,
                       pool_recycle=1800)
connections_opened = 0


@event.listens_for(engine, "connect")
def count_connection(*args):
    global connections_opened
    connections_opened += 1


def get_order(order_id: int):
    with engine.connect() as conn:                    # pinjam koneksi dari pool
        return conn.execute(text("SELECT * FROM orders WHERE id = :id"), {"id": order_id}).one()


if __name__ == "__main__":
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=10) as pool:  # 10 request bersamaan
        list(pool.map(get_order, range(1, 501)))
    print(f"500 request: {(time.perf_counter() - start) * 1000:.0f} ms, koneksi dibuka: {connections_opened}")
