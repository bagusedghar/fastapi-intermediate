"""Metrics - BEFORE (hanya rata-rata waktu response)

Middleware menghitung jumlah request dan rata-rata waktu response di dict biasa.
- Rata-rata menyembunyikan request yang lambat: terlihat cepat, padahal sebagian user menunggu lama
- Request yang error tidak dihitung terpisah
- Tidak ada pembagian per endpoint, dan angkanya hilang setiap aplikasi restart

Jalankan: python before.py
"""
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient

app = FastAPI()
stats = {"requests": 0, "total_ms": 0.0}


@app.middleware("http")
async def measure(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    stats["requests"] += 1
    stats["total_ms"] += (time.perf_counter() - start) * 1000
    return response


@app.get("/stats")
def get_stats():
    avg = stats["total_ms"] / stats["requests"]
    return {"requests": stats["requests"], "avg_ms": round(avg, 1)}


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    if order_id % 20 == 0:
        time.sleep(0.3)              # anggap: query lambat
    if order_id % 25 == 0:
        raise HTTPException(500, "database error")
    return {"id": order_id}


if __name__ == "__main__":
    client = TestClient(app, raise_server_exceptions=False)
    for order_id in range(1, 101):
        client.get(f"/orders/{order_id}")
    print("GET /stats ->", client.get("/stats").json())
