"""Infrastructure: config dari environment (Singleton lewat @lru_cache)."""
import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    database_url: str
    notification_channel: str


@lru_cache
def get_settings() -> Settings:
    return Settings(
        database_url=os.getenv("DATABASE_URL", "sqlite:///orders.db"),
        notification_channel=os.getenv("NOTIFICATION_CHANNEL", "email"),
    )
