"""Query Tuning - AFTER

Hitungan dipindah ke database dengan GROUP BY. Yang dikirim ke Python cuma hasil akhirnya.
Database memang dibuat untuk ini: filter, join, dan agregasi di dekat datanya.

Tips tuning lain yang sejenis:
- SELECT kolom yang dibutuhkan saja, bukan SELECT *
- Filter di WHERE, bukan di Python
- Hindari count(DISTINCT ...) di tabel besar: hitung total per order dulu di subquery
- Cek hasilnya lagi dengan EXPLAIN ANALYZE

Butuh PostgreSQL + data demo: docker compose up -d, lalu python seed_demo.py (dari folder sesi-07)
Jalankan demo: python after.py
"""
import os
import time

from sqlalchemy import create_engine, text

engine = create_engine(os.getenv("DEMO_DATABASE_URL", "postgresql+psycopg://app:app@localhost:5432/demo"))

SALES_BY_STATUS = text("""
    SELECT o.status, count(*) AS orders, sum(t.total) AS revenue
    FROM orders AS o
    JOIN (SELECT order_id, sum(price * qty) AS total      -- total per order dulu
          FROM order_lines GROUP BY order_id) AS t ON t.order_id = o.id
    GROUP BY o.status
""")


def sales_by_status(conn):
    rows = conn.execute(SALES_BY_STATUS).all()
    return {r.status: {"orders": r.orders, "revenue": int(r.revenue)} for r in rows}, len(rows)


if __name__ == "__main__":
    with engine.connect() as conn:
        start = time.perf_counter()
        report, rows = sales_by_status(conn)
        print(f"{rows} baris ke Python, {(time.perf_counter() - start) * 1000:.0f} ms")
        print("paid:", report["paid"])
