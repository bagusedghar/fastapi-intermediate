"""Health Checks - AFTER (liveness dan readiness dipisah)

- GET /health/live  : proses masih berjalan? Tidak mengecek dependency.
                      Jika gagal, Kubernetes me-restart container.
- GET /health/ready : siap menerima traffic? Mengecek database dan Redis.
                      Jika 503, load balancer berhenti mengirim traffic ke instance ini
                      sampai dependency pulih, tanpa restart.
Liveness sengaja tidak mengecek dependency: Redis mati tidak bisa diperbaiki dengan restart API.

Jalankan: python after.py
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from redis import Redis
from sqlalchemy import create_engine, text

engine = create_engine("sqlite://")                    # hidup
redis = Redis(port=6399, socket_connect_timeout=0.5,   # mati
              retry=None)
app = FastAPI()


def check_database() -> None:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))


def check_redis() -> None:
    redis.ping()


CHECKS = {"database": check_database, "redis": check_redis}


@app.get("/health/live")
def live():
    return {"status": "ok"}


@app.get("/health/ready")
def ready():
    results = {}
    for name, check in CHECKS.items():
        try:
            check()
            results[name] = "ok"
        except Exception as exc:
            results[name] = f"down: {type(exc).__name__}"
    healthy = all(r == "ok" for r in results.values())
    return JSONResponse(
        status_code=200 if healthy else 503,
        content={"status": "ready" if healthy else "not_ready",
                 "checks": results})


if __name__ == "__main__":
    client = TestClient(app, raise_server_exceptions=False)
    for path in ["/health/live", "/health/ready"]:
        response = client.get(path)
        print(f"GET {path:13} -> {response.status_code} "
              f"{response.text}")
