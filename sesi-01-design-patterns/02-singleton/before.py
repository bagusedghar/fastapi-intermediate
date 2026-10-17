"""Singleton - BEFORE

Setiap bagian aplikasi membuat object Settings sendiri.
Akibatnya config dibaca ulang berkali-kali, dan tiap bagian bisa memegang
object yang berbeda (misal satu sudah diubah, yang lain belum).
"""
import os


class Settings:
    def __init__(self):
        print("-> membaca config dari environment...")
        self.app_name = os.getenv("APP_NAME", "Order API")
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///orders.db")
        self.notification_channel = os.getenv("NOTIFICATION_CHANNEL", "email")


def connect_db():
    settings = Settings()
    print(f"connect ke {settings.database_url}")


def send_notification():
    settings = Settings()
    print(f"kirim via {settings.notification_channel}")


if __name__ == "__main__":
    connect_db()
    send_notification()
    print("object sama?", Settings() is Settings())  # False
