"""TTL & Invalidation - BEFORE

Cache disimpan tanpa TTL dan tidak pernah dihapus.
Harga di database sudah diubah, tapi API tetap mengembalikan harga lama dari cache.
Data basi (stale) ini akan bertahan selamanya, sampai Redis di-restart.

Butuh Redis: docker compose up -d
Jalankan demo: python before.py
"""
import json
import os

import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
cache = redis.Redis.from_url(REDIS_URL, decode_responses=True)

PRODUCTS = {1: {"id": 1, "name": "Keyboard", "price": 500_000}}


def get_product(product_id: int) -> dict:
    key = f"product:{product_id}"
    cached = cache.get(key)
    if cached is not None:
        return json.loads(cached)
    product = dict(PRODUCTS[product_id])
    cache.set(key, json.dumps(product))         # tanpa TTL
    return product


def update_price(product_id: int, price: int) -> None:
    PRODUCTS[product_id]["price"] = price       # cache tidak diubah


if __name__ == "__main__":
    cache.delete("product:1")
    print("Harga awal :", get_product(1)["price"])
    update_price(1, 450_000)
    print("Harga baru :", get_product(1)["price"])  # masih 500000
