"""Infrastructure: config dari environment (Singleton lewat @lru_cache)."""
import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    database_url: str
    notification_channel: str
    notification_fail_rate: float     # simulasi server email gangguan, 0.5 = setengah percobaan gagal
    broker_url: str
    result_backend: str
    task_always_eager: bool           # True = task langsung dijalankan tanpa worker (dipakai di test)
    report_delay: float               # simulasi report yang lama dibuat, dalam detik
    redis_url: str                    # Redis untuk cache dan rate limiter
    cache_ttl: int                    # detik
    rate_limit: int                   # jumlah request per window, per client
    rate_limit_window: int            # detik
    query_delay: float                # simulasi query produk yang berat, dalam detik


@lru_cache
def get_settings() -> Settings:
    return Settings(
        database_url=os.getenv("DATABASE_URL", "sqlite:///orders.db"),
        notification_channel=os.getenv("NOTIFICATION_CHANNEL", "email"),
        notification_fail_rate=float(os.getenv("NOTIFICATION_FAIL_RATE", "0")),
        broker_url=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
        result_backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1"),
        task_always_eager=os.getenv("CELERY_TASK_ALWAYS_EAGER", "0") == "1",
        report_delay=float(os.getenv("REPORT_DELAY", "5")),
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/2"),
        cache_ttl=int(os.getenv("CACHE_TTL", "60")),
        rate_limit=int(os.getenv("RATE_LIMIT", "20")),
        rate_limit_window=int(os.getenv("RATE_LIMIT_WINDOW", "60")),
        query_delay=float(os.getenv("QUERY_DELAY", "0.2")),
    )
