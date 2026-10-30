"""Aplikasi kecil untuk contoh multi-stage build. psycopg versi C butuh compiler saat di-install."""
import psycopg
from fastapi import FastAPI

app = FastAPI()


@app.get("/health/live")
def live():
    return {"status": "ok", "psycopg": psycopg.__version__}
