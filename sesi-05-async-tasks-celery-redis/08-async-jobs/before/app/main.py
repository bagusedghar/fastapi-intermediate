"""Order API - titik awal Sesi 5 (hasil akhir Sesi 4)

Jalankan dari folder before/: uvicorn app.main:app --reload
"""
from fastapi import FastAPI

from app.api.errors import register_exception_handlers
from app.api.middleware import log_requests
from app.api.routers import orders, products

app = FastAPI(
    title="Order API",
    version="1.0.0",
    description="API untuk mengelola produk dan order. Semua error memakai format `{\"error\": {...}}`.",
    openapi_tags=[
        {"name": "products", "description": "Data produk dan stok"},
        {"name": "orders", "description": "Membuat, membayar, dan membatalkan order"},
    ],
)

app.middleware("http")(log_requests)
register_exception_handlers(app)
app.include_router(products.router)
app.include_router(orders.router)
