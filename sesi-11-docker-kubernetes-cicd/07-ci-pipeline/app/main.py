"""Aplikasi kecil untuk contoh pipeline CI. Ada satu import yang tidak dipakai (sengaja, untuk lint)."""
import os

from fastapi import FastAPI

app = FastAPI()


@app.get("/health/live")
def live():
    return {"status": "ok"}
