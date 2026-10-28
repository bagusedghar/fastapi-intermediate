"""Rate Limiting - AFTER (fixed window)

Setiap client maksimal 10 request per menit.
Counter disimpan di Redis per client per menit: INCR menambah 1, EXPIRE menghapusnya setelah menit berakhir.
Lewat batas = 429 Too Many Requests, dengan header Retry-After (berapa detik lagi boleh mencoba).

Counter ada di Redis, bukan di memory, supaya limit tetap berlaku walaupun API dijalankan di banyak server.

Butuh Redis: docker compose up -d
Jalankan demo: python after.py
Atau server:   uvicorn after:app --reload
"""
import os
import time

import redis
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.testclient import TestClient

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
cache = redis.Redis.from_url(REDIS_URL, decode_responses=True)
app = FastAPI()

LIMIT, WINDOW = 10, 60            # 10 request per 60 detik


def rate_limit(request: Request) -> None:
    now = int(time.time())
    key = f"ratelimit:{request.client.host}:{now // WINDOW}"
    count = cache.incr(key)
    if count == 1:
        cache.expire(key, WINDOW)
    if count > LIMIT:
        retry_after = str(WINDOW - now % WINDOW)
        raise HTTPException(429, "Terlalu banyak request",
                            headers={"Retry-After": retry_after})


@app.post("/orders", status_code=201,
          dependencies=[Depends(rate_limit)])
def create_order():
    return {"message": "Order dibuat"}


if __name__ == "__main__":
    for key in cache.scan_iter("ratelimit:*"):
        cache.delete(key)
    client = TestClient(app)
    codes = [client.post("/orders").status_code for _ in range(15)]
    print("Status code:", codes)        # 10x 201, lalu 5x 429
