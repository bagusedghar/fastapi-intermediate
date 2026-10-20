"""Order API - titik awal Sesi 3 (hasil akhir Sesi 2)

Jalankan dari folder before/: uvicorn app.main:app --reload
"""
from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(title="Order API")
app.include_router(router)
