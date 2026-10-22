"""Order API - titik awal Sesi 7 (hasil akhir Sesi 6)

Jalankan dari folder before/, masing-masing di terminal sendiri:
    docker compose up -d                                   (PostgreSQL + Redis, dari folder sesi-07)
    celery -A app.worker.celery_app worker --loglevel=info --pool=solo
    uvicorn app.main:app --reload

Bandingkan latency dengan dan tanpa cache: python benchmark.py

Tambahan untuk Sesi 7 (tidak mengubah aplikasi):
    python seed.py               isi PostgreSQL dengan 20.000 order
    python profile_queries.py    ukur waktu dan jumlah query
"""
from fastapi import FastAPI

from app.api.errors import register_exception_handlers
from app.api.middleware import log_requests
from app.api.routers import orders, products, reports

app = FastAPI(
    title="Order API",
    version="1.0.0",
    description="API untuk mengelola produk dan order. Semua error memakai format `{\"error\": {...}}`.",
    openapi_tags=[
        {"name": "products", "description": "Data produk dan stok (di-cache di Redis)"},
        {"name": "orders", "description": "Membuat, membayar, dan membatalkan order (dibatasi rate limit)"},
        {"name": "reports", "description": "Report penjualan, dibuat di background oleh worker"},
    ],
)

app.middleware("http")(log_requests)
register_exception_handlers(app)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(reports.router)
