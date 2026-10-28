"""Infrastructure: adapter Redis untuk port Cache.

Nilai disimpan sebagai JSON. TTL ditambah jitter (acak sampai 10%),
supaya key yang dibuat bersamaan tidak kedaluwarsa di detik yang sama (mengurangi cache stampede).
"""
import json
import random

from redis import Redis


class RedisCache:
    def __init__(self, redis: Redis, ttl: int):
        self.redis = redis
        self.ttl = ttl

    def get(self, key: str):
        value = self.redis.get(key)
        return None if value is None else json.loads(value)

    def set(self, key: str, value) -> None:
        jitter = random.randint(0, max(1, self.ttl // 10))
        self.redis.set(key, json.dumps(value), ex=self.ttl + jitter)

    def delete(self, *keys: str) -> None:
        if keys:
            self.redis.delete(*keys)
