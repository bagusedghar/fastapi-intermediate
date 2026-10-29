"""Secrets - BEFORE (secret ditulis di kode)

- Secret JWT dan password database ada di source code, jadi ikut ter-commit ke Git dan
  terbaca oleh siapa pun yang punya akses repository
- Mengganti secret berarti mengubah kode dan deploy ulang
- Saat config dicetak ke log untuk debugging, semua secret ikut tercetak

Jalankan: python before.py
"""
from dataclasses import dataclass


@dataclass
class Settings:
    database_url: str = "postgresql://app:rahasia123@db.internal/orders"
    jwt_secret: str = "secret"
    debug: bool = True


if __name__ == "__main__":
    settings = Settings()
    print("Config saat startup:", settings)
