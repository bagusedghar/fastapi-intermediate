"""Secrets - AFTER (secret dari environment, divalidasi saat startup)

pydantic-settings membaca config dari environment variable (dan file .env saat development):
- Field tanpa default = WAJIB ada. Jika tidak di-set, aplikasi gagal start dengan pesan jelas
- SecretStr menyembunyikan nilai saat dicetak atau masuk log. Nilai asli dibaca dengan .get_secret_value()
- min_length=32 menolak secret yang terlalu pendek dan mudah ditebak
File .env tidak di-commit (masuk .gitignore). Yang di-commit hanya .env.example tanpa nilai asli.

Jalankan: python after.py
"""
import os

from pydantic import Field, SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: SecretStr
    jwt_secret: SecretStr = Field(min_length=32)
    debug: bool = False


if __name__ == "__main__":
    try:
        Settings()
    except ValidationError as exc:
        print("Tanpa environment variable:")
        for error in exc.errors():
            print(f"  {error['loc'][0]}: {error['msg']}")

    os.environ["DATABASE_URL"] = "postgresql://app:rahasia123@db/orders"
    os.environ["JWT_SECRET"] = "3f9a1c7e5b2d8f4a6c0e9b1d7f3a5c8e"
    settings = Settings()
    print("Config saat startup:", settings)
    secret = settings.jwt_secret.get_secret_value()
    print("Dipakai di kode    :", secret[:6] + "...")
