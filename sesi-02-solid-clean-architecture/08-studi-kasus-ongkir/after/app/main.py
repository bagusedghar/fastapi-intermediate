"""Order API - AFTER studi kasus (ongkos kirim)

Jalankan dari folder after/: uvicorn app.main:app --reload
"""
from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(title="Order API")
app.include_router(router)
