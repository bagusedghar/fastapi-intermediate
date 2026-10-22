"""Cache Stampede - AFTER

- Lock     : hanya request yang berhasil mengambil lock (SET NX) yang query ke database.
             Request lain menunggu sebentar, lalu membaca cache yang sudah diisi.
- Jitter   : TTL ditambah angka acak, supaya banyak key tidak kedaluwarsa di detik yang sama.

Butuh Redis: docker compose up -d
Jalankan demo: python after.py
"""
import json
import os
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import redis

cache = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)

PRODUCTS = {1: {"id": 1, "name": "Keyboard", "price": 500_000}}
db_queries = 0
counter_lock = threading.Lock()


def query_product(product_id: int) -> dict:
    global db_queries
    with counter_lock:
        db_queries += 1
    time.sleep(0.5)
    return dict(PRODUCTS[product_id])


def get_product(product_id: int) -> dict:
    key = f"product:{product_id}"
    while True:
        cached = cache.get(key)
        if cached is not None:
            return json.loads(cached)

        if cache.set(f"lock:{key}", "1", nx=True, ex=5):         # hanya satu yang dapat lock
            try:
                product = query_product(product_id)
                cache.set(key, json.dumps(product), ex=60 + random.randint(0, 10))   # TTL + jitter
                return product
            finally:
                cache.delete(f"lock:{key}")

        time.sleep(0.05)                            # yang lain menunggu, lalu cek cache lagi


if __name__ == "__main__":
    cache.delete("product:1")
    with ThreadPoolExecutor(max_workers=20) as pool:
        list(pool.map(get_product, [1] * 20))
    print("Query ke database:", db_queries)         # 1
