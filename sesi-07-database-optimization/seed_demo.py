"""Isi database demo untuk contoh 01-06.

200 produk, 200.000 order, dan 400.000 item order. Data dibuat langsung di PostgreSQL
dengan generate_series, jadi cukup sekitar 15 detik.
Tabel sengaja dibuat TANPA index selain primary key, supaya masalahnya terlihat.

Butuh PostgreSQL: docker compose up -d
Jalankan sekali dari folder sesi-07: python seed_demo.py
"""
import os
import time

from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DEMO_DATABASE_URL", "postgresql+psycopg://app:app@localhost:5432/demo")

SCHEMA = """
DROP TABLE IF EXISTS order_lines, orders, products;

CREATE TABLE products (
    id    serial PRIMARY KEY,
    name  varchar(100) NOT NULL,
    price integer NOT NULL
);

CREATE TABLE orders (
    id         serial PRIMARY KEY,
    customer   varchar(100) NOT NULL,
    status     varchar(20) NOT NULL,
    created_at timestamp NOT NULL
);

CREATE TABLE order_lines (
    id         serial PRIMARY KEY,
    order_id   integer NOT NULL REFERENCES orders (id),
    product_id integer NOT NULL REFERENCES products (id),
    price      integer NOT NULL,
    qty        integer NOT NULL
);
"""

SEED = """
INSERT INTO products (name, price)
SELECT 'Produk ' || g, 10000 + (g * 7919) % 990000
FROM generate_series(1, 200) AS g;

INSERT INTO orders (customer, status, created_at)
SELECT 'customer' || (g % 5000) || '@mail.com',
       (ARRAY['pending', 'paid', 'paid', 'cancelled'])[1 + g % 4],
       timestamp '2026-01-01' + g * interval '1 minute'
FROM generate_series(1, 200000) AS g;

INSERT INTO order_lines (order_id, product_id, price, qty)
SELECT o.id, p.id, p.price, 1 + (o.id + n) % 3
FROM orders AS o
CROSS JOIN generate_series(1, 2) AS n
JOIN products AS p ON p.id = 1 + (o.id * 7 + n) % 200;

ANALYZE;
"""

if __name__ == "__main__":
    start = time.perf_counter()
    engine = create_engine(DATABASE_URL)
    with engine.begin() as conn:
        conn.execute(text(SCHEMA))
        conn.execute(text(SEED))
        counts = {table: conn.execute(text(f"SELECT count(*) FROM {table}")).scalar()
                  for table in ("products", "orders", "order_lines")}
    print(counts, f"selesai dalam {time.perf_counter() - start:.1f} detik")
