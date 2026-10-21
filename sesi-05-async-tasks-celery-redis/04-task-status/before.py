"""Task Status - BEFORE

Status job disimpan di dict JOBS. Kelihatannya benar, tapi API dan worker adalah dua proses berbeda.
Worker mengubah JOBS miliknya sendiri, JOBS di proses API tidak ikut berubah.
Hasilnya status di API selamanya "pending", dan hasil report tidak bisa diambil.

Jalankan 3 hal, masing-masing di terminal sendiri:
    docker compose up -d
    celery -A before:celery_app worker --loglevel=info --pool=solo
    uvicorn before:app --reload
"""
import time
from uuid import uuid4

from celery import Celery
from fastapi import FastAPI

celery_app = Celery("demo", broker="redis://localhost:6379/0")
app = FastAPI()
JOBS: dict[str, str] = {}             # memory proses API


@celery_app.task
def generate_sales_report(job_id: str, month: str) -> dict:
    JOBS[job_id] = "running"          # ini memory proses WORKER, bukan API
    time.sleep(10)
    JOBS[job_id] = "done"
    return {"month": month, "orders": 120, "revenue": 54_000_000}


@app.post("/reports/sales", status_code=202)
def create_sales_report(month: str):
    job_id = uuid4().hex
    JOBS[job_id] = "pending"
    generate_sales_report.delay(job_id, month)
    return {"job_id": job_id}


@app.get("/reports/{job_id}")
def get_report(job_id: str):
    return {"job_id": job_id, "status": JOBS.get(job_id)}     # selalu "pending"
