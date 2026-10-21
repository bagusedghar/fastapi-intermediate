"""Middleware - AFTER

Middleware membungkus SEMUA request:
request masuk -> middleware -> route -> middleware -> response keluar.
Logging dan header X-Process-Time cukup ditulis sekali, dan route tetap simple.

Jalankan: uvicorn after:app --reload
"""
import time

from fastapi import FastAPI, Request

app = FastAPI()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)          # lanjut ke route
    ms = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time"] = f"{ms:.1f}ms"
    print(f"{request.method} {request.url.path} {response.status_code} {ms:.1f}ms")
    return response


@app.get("/products")
def list_products():
    return [{"id": 1, "name": "Keyboard"}]


@app.get("/orders")
def list_orders():
    return [{"id": 1, "customer": "budi@mail.com"}]


@app.get("/health")
def health():
    return {"status": "ok"}
