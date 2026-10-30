"""Aplikasi demo untuk contoh Kubernetes 04-06.

- GET /             : nama pod yang menjawab, pesan dari MESSAGE, dan apakah API_KEY ada
- GET /health/live  : 500 setelah BREAK_AFTER detik (simulasi aplikasi macet), selain itu 200
- GET /health/ready : 503 selama STARTUP_SECONDS detik pertama (simulasi startup lambat)
"""
import os
import socket
import time

from fastapi import FastAPI
from fastapi.responses import JSONResponse

STARTED = time.time()
STARTUP_SECONDS = float(os.getenv("STARTUP_SECONDS", "0"))
BREAK_AFTER = float(os.getenv("BREAK_AFTER", "0"))          # 0 = tidak pernah macet
app = FastAPI()


def uptime() -> float:
    return time.time() - STARTED


@app.get("/")
def index():
    return {"pod": socket.gethostname(), "message": os.getenv("MESSAGE", "-"),
            "api_key_set": bool(os.getenv("API_KEY"))}


@app.get("/health/live")
def live():
    if BREAK_AFTER and uptime() > BREAK_AFTER:
        return JSONResponse(status_code=500, content={"status": "macet"})
    return {"status": "ok"}


@app.get("/health/ready")
def ready():
    if uptime() < STARTUP_SECONDS:
        return JSONResponse(status_code=503, content={"status": "starting"})
    return {"status": "ready"}
