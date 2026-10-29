"""Health Checks - BEFORE (/health selalu "ok")

Endpoint /health hanya mengembalikan "ok" tanpa mengecek apa pun.
Redis sedang mati (port 6399 tidak ada yang mendengarkan), jadi endpoint produk error.
Load balancer atau Kubernetes melihat /health = 200, lalu tetap mengirim traffic ke instance ini.

Jalankan: python before.py
"""
from fastapi import FastAPI
from fastapi.testclient import TestClient
from redis import Redis
from sqlalchemy import create_engine, text

engine = create_engine("sqlite://")                    # hidup
redis = Redis(port=6399, socket_connect_timeout=0.5,   # mati
              retry=None)
app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/products")
def list_products():
    cached = redis.get("products")             # cek cache dulu
    if cached is None:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))     # anggap: query produk
    return {"products": []}


if __name__ == "__main__":
    client = TestClient(app, raise_server_exceptions=False)
    for path in ["/health", "/products"]:
        response = client.get(path)
        print(f"GET {path:9} -> {response.status_code} {response.text}")
