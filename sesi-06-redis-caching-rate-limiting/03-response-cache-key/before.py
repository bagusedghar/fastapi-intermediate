"""Response Cache & Cache Key - BEFORE

Response GET /products di-cache dengan key "products" untuk semua request.
Padahal hasilnya bergantung pada query parameter (category, page).
Request kategori "mouse" malah mendapat response kategori "keyboard" yang lebih dulu tersimpan.

Butuh Redis: docker compose up -d
Jalankan demo: python before.py
Atau server:   uvicorn before:app --reload
"""
import json
import os

import redis
from fastapi import FastAPI
from fastapi.testclient import TestClient

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
cache = redis.Redis.from_url(REDIS_URL, decode_responses=True)
app = FastAPI()

PRODUCTS = [
    {"id": 1, "name": "Keyboard Mekanik", "category": "keyboard"},
    {"id": 2, "name": "Keyboard Wireless", "category": "keyboard"},
    {"id": 3, "name": "Mouse Gaming", "category": "mouse"},
]


def query_products(category: str | None, page: int) -> list[dict]:
    rows = [p for p in PRODUCTS if category in (None, p["category"])]
    return rows[(page - 1) * 2: page * 2]        # 2 produk per page


@app.get("/products")
def list_products(category: str | None = None, page: int = 1):
    cached = cache.get("products")      # key sama untuk semua query
    if cached is not None:
        return json.loads(cached)
    result = query_products(category, page)
    cache.set("products", json.dumps(result), ex=60)
    return result


if __name__ == "__main__":
    cache.delete("products")
    client = TestClient(app)
    for url in ["/products?category=keyboard",
                "/products?category=mouse"]:
        names = [p["name"] for p in client.get(url).json()]
        print(f"{url:28}", names)       # mouse dapat keyboard
