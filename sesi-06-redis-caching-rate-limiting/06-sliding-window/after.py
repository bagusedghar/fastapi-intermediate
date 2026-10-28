"""Sliding Window - AFTER (sliding window log)

Setiap request dicatat waktunya di Redis sorted set (score = waktu request).
Yang dihitung selalu request dalam 60 detik terakhir dari SEKARANG, bukan per menit di jam dinding.
Jadi tidak ada celah di pergantian menit.

Trade-off: memakai memory lebih banyak (satu entry per request), sedangkan fixed window cuma satu angka.

Butuh Redis: docker compose up -d
Jalankan demo: python after.py
"""
import os
from uuid import uuid4

import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
cache = redis.Redis.from_url(REDIS_URL, decode_responses=True)

LIMIT, WINDOW = 10, 60


def allow(client_id: str, now: float) -> bool:
    key = f"sliding:{client_id}"
    cache.zremrangebyscore(key, 0, now - WINDOW)   # buang yang > 60s
    if cache.zcard(key) >= LIMIT:
        return False
    cache.zadd(key, {uuid4().hex: now})            # catat request ini
    cache.expire(key, WINDOW)
    return True


if __name__ == "__main__":
    cache.delete("sliding:budi")
    accepted = sum(allow("budi", now=59.0) for _ in range(10))
    accepted += sum(allow("budi", now=60.5) for _ in range(10))
    print(f"Diterima dalam 2 detik: {accepted} (limit 10/menit)")  # 10
    print("Detik ke-119:", allow("budi", now=119.5))  # True
