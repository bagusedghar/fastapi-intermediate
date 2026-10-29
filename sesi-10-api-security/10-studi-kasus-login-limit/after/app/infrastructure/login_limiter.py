"""Infrastructure: pembatas login gagal per email di Redis (adapter port LoginAttemptLimiter).

Key v1:login-fail:<email> berisi jumlah login gagal.
- Gagal pertama: key dibuat dengan masa berlaku block_seconds (fixed window)
- Jumlah gagal >= max_attempts: login dengan email itu ditolak sampai key kedaluwarsa
- Login berhasil: key dihapus
Dihitung per email, bukan per IP, karena penyerang bisa berganti IP tetapi menyerang akun yang sama.
Setiap kegagalan dicatat di log (tanpa password) dan metric login_failures_total.
"""
import logging

from redis import Redis

from app.infrastructure.metrics import LOGIN_BLOCKED, LOGIN_FAILURES

logger = logging.getLogger("app.auth")


class RedisLoginAttemptLimiter:
    def __init__(self, redis: Redis, max_attempts: int, block_seconds: int):
        self.redis = redis
        self.max_attempts = max_attempts
        self.block_seconds = block_seconds

    @staticmethod
    def key(email: str) -> str:
        return f"v1:login-fail:{email.strip().lower()}"

    def blocked_for(self, email: str) -> int:
        failures = int(self.redis.get(self.key(email)) or 0)
        if failures < self.max_attempts:
            return 0
        LOGIN_BLOCKED.inc()
        logger.warning("login diblokir", extra={"email": email, "error_type": "client"})
        return max(self.redis.ttl(self.key(email)), 1)

    def record_failure(self, email: str) -> None:
        key = self.key(email)
        failures = self.redis.incr(key)
        if failures == 1:
            self.redis.expire(key, self.block_seconds)
        LOGIN_FAILURES.inc()
        logger.warning("login gagal", extra={"email": email, "failures": failures, "error_type": "client"})

    def reset(self, email: str) -> None:
        self.redis.delete(self.key(email))
