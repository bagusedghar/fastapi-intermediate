"""Sliding Window - BEFORE (fixed window)

Limit 10 request per menit dengan fixed window (counter per menit, seperti 05-rate-limiting).
Masalahnya ada di pergantian menit: 10 request di detik ke-59 dan 10 request di detik ke-60
masuk ke dua window yang berbeda. Hasilnya 20 request lolos dalam 2 detik.

Waktu disimulasikan lewat parameter `now`, supaya demo tidak perlu menunggu satu menit.

Butuh Redis: docker compose up -d
Jalankan demo: python before.py
"""
import os

import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
cache = redis.Redis.from_url(REDIS_URL, decode_responses=True)

LIMIT, WINDOW = 10, 60


def allow(client_id: str, now: float) -> bool:
    key = f"fixed:{client_id}:{int(now // WINDOW)}"
    count = cache.incr(key)
    if count == 1:
        cache.expire(key, WINDOW)
    return count <= LIMIT


if __name__ == "__main__":
    for key in cache.scan_iter("fixed:budi:*"):
        cache.delete(key)
    accepted = sum(allow("budi", now=59.0) for _ in range(10))
    accepted += sum(allow("budi", now=60.5) for _ in range(10))
    print(f"Diterima dalam 2 detik: {accepted} (limit 10/menit)")  # 20
