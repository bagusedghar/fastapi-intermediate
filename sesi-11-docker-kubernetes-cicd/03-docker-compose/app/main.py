"""Aplikasi kecil untuk contoh Docker Compose: readiness check ke PostgreSQL dan Redis."""
import os

import psycopg
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from redis import Redis

DB_URL = os.environ["DATABASE_URL"]
REDIS_URL = os.environ["REDIS_URL"]
app = FastAPI()


def check(fn) -> str:
    try:
        fn()
        return "ok"
    except Exception as exc:
        return f"down: {type(exc).__name__}"


@app.get("/health/ready")
def ready():
    checks = {
        "database": check(lambda: psycopg.connect(DB_URL, connect_timeout=2).close()),
        "redis": check(lambda: Redis.from_url(REDIS_URL, socket_connect_timeout=2).ping()),
    }
    ok = all(v == "ok" for v in checks.values())
    return JSONResponse(status_code=200 if ok else 503, content=checks)
