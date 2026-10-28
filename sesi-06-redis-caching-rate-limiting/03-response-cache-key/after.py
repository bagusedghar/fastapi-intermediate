"""Response Cache & Cache Key - AFTER

Cache key yang baik:
- punya namespace     : "products:list", supaya tidak bentrok dengan data lain di Redis
- punya versi         : "v1", kalau bentuk response berubah cukup naikkan ke v2
- memuat semua parameter yang memengaruhi hasil (category, page)
- dinormalisasi       : category kosong = "all", page default = 1, jadi request yang sama dapat key yang sama

Header X-Cache (HIT/MISS) membantu mengecek cache bekerja atau tidak.

Butuh Redis: docker compose up -d
Jalankan demo: python after.py
Atau server:   uvicorn after:app --reload
"""
import json
import os

import redis
from fastapi import FastAPI, Response
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


def products_key(category: str | None, page: int) -> str:
    return f"v1:products:list:category={category or 'all'}:page={page}"


@app.get("/products")
def list_products(response: Response,
                  category: str | None = None, page: int = 1):
    key = products_key(category, page)
    cached = cache.get(key)
    if cached is not None:
        response.headers["X-Cache"] = "HIT"
        return json.loads(cached)

    result = query_products(category, page)
    cache.set(key, json.dumps(result), ex=60)
    response.headers["X-Cache"] = "MISS"
    return result


if __name__ == "__main__":
    for key in cache.scan_iter("v1:products:list:*"):
        cache.delete(key)
    client = TestClient(app)
    for url in ["/products?category=keyboard",
                "/products?category=mouse",
                "/products?category=mouse"]:
        r = client.get(url)
        names = [p["name"] for p in r.json()]
        print(f"{url:28} {r.headers['X-Cache']:4}", names)
