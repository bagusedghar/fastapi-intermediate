"""Order API - titik awal studi kasus (hasil hands-on Sesi 2)

Tugas: tambahkan ongkos kirim. Soal lengkapnya ada di README.md folder 08-studi-kasus-ongkir.
Jalankan dari folder before/: uvicorn app.main:app --reload
"""
from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(title="Order API")
app.include_router(router)
