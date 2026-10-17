"""Singleton: config dibaca sekali, dipakai di mana saja lewat get_settings()."""
import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    database_path: str
    notification_channel: str


@lru_cache
def get_settings() -> Settings:
    return Settings(
        database_path=os.getenv("DATABASE_PATH", "orders.db"),
        notification_channel=os.getenv("NOTIFICATION_CHANNEL", "email"),
    )
