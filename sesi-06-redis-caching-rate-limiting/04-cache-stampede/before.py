"""Cache Stampede - BEFORE

Produk yang sedang promo dibuka ribuan orang. Saat cache-nya kedaluwarsa,
semua request yang datang bersamaan mendapat cache miss dan semuanya query ke database.
Database yang tadinya santai mendadak menerima lonjakan query (stampede).

Butuh Redis: docker compose up -d
Jalankan demo: python before.py
"""
import json
import os
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
    cached = cache.get(key)
    if cached is not None:
        return json.loads(cached)
    product = query_product(product_id)
    cache.set(key, json.dumps(product), ex=60)
    return product


if __name__ == "__main__":
    cache.delete("product:1")                       # anggap: cache baru saja kedaluwarsa
    with ThreadPoolExecutor(max_workers=20) as pool:
        list(pool.map(get_product, [1] * 20))       # 20 request bersamaan
    print("Query ke database:", db_queries)         # 20
