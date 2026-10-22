"""TTL & Invalidation - AFTER

Dua lapis pengaman supaya cache tidak basi:
- Invalidation : setiap data berubah, key cache-nya dihapus. Request berikutnya mengisi ulang dari database.
- TTL          : kalau ada perubahan yang lupa meng-invalidate, cache tetap kedaluwarsa sendiri.

Menghapus key lebih aman daripada menimpa isinya, karena isi baru selalu diambil langsung dari database.

Butuh Redis: docker compose up -d
Jalankan demo: python after.py
"""
import json
import os

import redis

cache = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)

PRODUCTS = {1: {"id": 1, "name": "Keyboard", "price": 500_000}}
TTL = 60


def get_product(product_id: int) -> dict:
    key = f"product:{product_id}"
    cached = cache.get(key)
    if cached is not None:
        return json.loads(cached)
    product = dict(PRODUCTS[product_id])
    cache.set(key, json.dumps(product), ex=TTL)     # kedaluwarsa setelah 60 detik
    return product


def update_price(product_id: int, price: int) -> None:
    PRODUCTS[product_id]["price"] = price
    cache.delete(f"product:{product_id}")           # invalidation


if __name__ == "__main__":
    cache.delete("product:1")
    print("Harga awal :", get_product(1)["price"])
    update_price(1, 450_000)
    print("Harga baru :", get_product(1)["price"])  # 450000
    print("Sisa TTL   :", cache.ttl("product:1"), "detik")
