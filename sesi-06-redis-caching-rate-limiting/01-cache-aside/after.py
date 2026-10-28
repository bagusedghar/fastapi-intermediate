"""Cache-Aside - AFTER

Aplikasi cek cache dulu:
- ada (cache hit)     -> langsung pakai, database tidak disentuh
- tidak ada (miss)    -> query database, simpan hasilnya ke cache dengan TTL, lalu kembalikan
Yang mengatur cache adalah aplikasi, database tidak tahu ada cache.

Butuh Redis: docker compose up -d (dari folder sesi-06)
Jalankan demo: python after.py
"""
import json
import os
import time

import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
cache = redis.Redis.from_url(REDIS_URL, decode_responses=True)

PRODUCTS = {1: {"id": 1, "name": "Keyboard", "price": 500_000}}
db_queries = 0


def query_product(product_id: int) -> dict:
    global db_queries
    db_queries += 1
    time.sleep(0.5)
    return dict(PRODUCTS[product_id])


def get_product(product_id: int) -> dict:
    key = f"product:{product_id}"
    cached = cache.get(key)
    if cached is not None:                  # cache hit
        return json.loads(cached)

    product = query_product(product_id)     # cache miss
    cache.set(key, json.dumps(product), ex=60)    # TTL 60 detik
    return product


if __name__ == "__main__":
    cache.delete("product:1")               # mulai dari cache kosong
    start = time.perf_counter()
    for _ in range(5):
        get_product(1)
    took = time.perf_counter() - start
    print(f"5 request: {took:.1f} detik, "
          f"query ke database: {db_queries}")    # 0.5 detik, 1
