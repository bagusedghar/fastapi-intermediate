"""Singleton - AFTER

Di Python, cara paling simpel bikin singleton adalah function + @lru_cache.
Pemanggilan pertama membuat object, pemanggilan berikutnya mengembalikan object yang sama.
Cara ini juga yang dipakai di dokumentasi FastAPI untuk settings.
"""
import os
from functools import lru_cache


class Settings:
    def __init__(self):
        print("-> membaca config dari environment...")
        self.app_name = os.getenv("APP_NAME", "Order API")
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///orders.db")
        self.notification_channel = os.getenv("NOTIFICATION_CHANNEL", "email")


@lru_cache
def get_settings() -> Settings:
    return Settings()


def connect_db():
    print(f"connect ke {get_settings().database_url}")


def send_notification():
    print(f"kirim via {get_settings().notification_channel}")


if __name__ == "__main__":
    connect_db()
    send_notification()
    print("object sama?", get_settings() is get_settings())  # True

    # Di test, kalau perlu config lain: ubah env lalu kosongkan cache
    os.environ["NOTIFICATION_CHANNEL"] = "sms"
    get_settings.cache_clear()
    send_notification()
