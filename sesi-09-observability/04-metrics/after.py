"""Metrics - AFTER (Prometheus: counter dan histogram)

Library prometheus_client mencatat dua metric, dikelompokkan dengan label:
- Counter   http_requests_total            : jumlah request per route dan status
- Histogram http_request_duration_seconds  : sebaran waktu response per route, dalam bucket
Endpoint GET /metrics menampilkan semua angka dalam format teks Prometheus.
Prometheus server mengambil (scrape) endpoint ini berkala, lalu Grafana menampilkannya sebagai grafik.

Label route memakai pola path ("/orders/{order_id}"), bukan path asli ("/orders/7"),
supaya jumlah kombinasi label tetap sedikit.

Jalankan: python after.py
"""
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient
from prometheus_client import (CONTENT_TYPE_LATEST, Counter, Histogram,
                               generate_latest)
from starlette.responses import Response

REQUESTS = Counter("http_requests_total", "Jumlah request",
                   ["method", "route", "status"])
LATENCY = Histogram("http_request_duration_seconds",
                    "Waktu response", ["route"],
                    buckets=[0.05, 0.1, 0.25, 0.5, 1])
app = FastAPI()


@app.middleware("http")
async def measure(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    route = request.scope.get("route")
    path = route.path if route else "unknown"   # pola, bukan path asli
    REQUESTS.labels(request.method, path, response.status_code).inc()
    LATENCY.labels(path).observe(time.perf_counter() - start)
    return response


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


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
    print("GET /metrics (potongan):")
    for line in client.get("/metrics").text.splitlines():
        if line.startswith(("http_requests_total{",
                            "http_request_duration_seconds_bucket")):
            if "/orders/" in line:
                print(" ", line)
