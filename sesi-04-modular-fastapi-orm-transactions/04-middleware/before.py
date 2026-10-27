"""Middleware - BEFORE

Kita ingin mencatat setiap request: method, path, status, dan berapa lama prosesnya.
Kodenya ditempel di setiap route. Route baru lupa ditempel = tidak tercatat,
dan request yang error tidak tercatat sama sekali.

Jalankan: uvicorn before:app --reload
"""
import time

from fastapi import FastAPI

app = FastAPI()


@app.get("/products")
def list_products():
    start = time.perf_counter()
    result = [{"id": 1, "name": "Keyboard"}]
    ms = (time.perf_counter() - start) * 1000
    print(f"GET /products 200 {ms:.1f}ms")
    return result


@app.get("/orders")
def list_orders():
    start = time.perf_counter()
    result = [{"id": 1, "customer": "budi@mail.com"}]
    ms = (time.perf_counter() - start) * 1000
    print(f"GET /orders 200 {ms:.1f}ms")
    return result


@app.get("/health")
def health():                           # lupa ditambahkan logging
    return {"status": "ok"}
