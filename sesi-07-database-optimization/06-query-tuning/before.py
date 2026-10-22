"""Query Tuning - BEFORE

Report penjualan per status order.
Semua order dan semua item diambil ke Python, lalu dihitung dengan loop.
600.000 baris dikirim lewat jaringan dan disimpan di memory, padahal hasil akhirnya cuma 3 baris.

Butuh PostgreSQL + data demo: docker compose up -d, lalu python seed_demo.py (dari folder sesi-07)
Jalankan demo: python before.py
"""
import os
import time
from collections import defaultdict

from sqlalchemy import create_engine, text

engine = create_engine(os.getenv("DEMO_DATABASE_URL", "postgresql+psycopg://app:app@localhost:5432/demo"))


def sales_by_status(conn):
    orders = conn.execute(text("SELECT * FROM orders")).all()
    lines = conn.execute(text("SELECT * FROM order_lines")).all()

    status_of = {o.id: o.status for o in orders}
    report = defaultdict(lambda: {"orders": 0, "revenue": 0})
    for o in orders:
        report[o.status]["orders"] += 1
    for line in lines:
        report[status_of[line.order_id]]["revenue"] += line.price * line.qty
    return dict(report), len(orders) + len(lines)


if __name__ == "__main__":
    with engine.connect() as conn:
        start = time.perf_counter()
        report, rows = sales_by_status(conn)
        print(f"{rows} baris ke Python, {(time.perf_counter() - start) * 1000:.0f} ms")
        print("paid:", report["paid"])
