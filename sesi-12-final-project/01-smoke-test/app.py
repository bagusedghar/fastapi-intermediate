"""Aplikasi demo untuk contoh smoke test: versi yang baru di-deploy, tetapi DATABASE_URL lupa di-set.

Proses tetap jalan dan /health/live tetap 200, tetapi setiap fitur yang butuh database gagal.
"""
import os

from fastapi import FastAPI, HTTPException

app = FastAPI()
DATABASE_URL = os.getenv("DATABASE_URL")           # lupa di-set saat deploy
TOKENS = {"budi@mail.com": "token-budi"}


@app.get("/health/live")
def live():
    return {"status": "ok"}


@app.get("/health/ready")
def ready():
    if not DATABASE_URL:
        raise HTTPException(503, "database belum dikonfigurasi")
    return {"status": "ready"}


@app.post("/auth/token")
def login(username: str, password: str):
    if not DATABASE_URL:
        raise HTTPException(500, "Internal Server Error")
    return {"access_token": TOKENS[username], "token_type": "bearer"}
