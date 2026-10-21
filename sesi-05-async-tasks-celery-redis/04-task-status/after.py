"""Task Status - AFTER

Status dan hasil task dicatat Celery di result backend (Redis),
jadi API dan worker membaca data yang sama.

Status Celery:
    PENDING  -> belum diambil worker (atau task_id tidak dikenal)
    STARTED  -> sedang dikerjakan (perlu task_track_started=True)
    RETRY    -> gagal, menunggu dicoba lagi
    SUCCESS  -> selesai, hasilnya ada di result.result
    FAILURE  -> gagal, error-nya ada di result.result

Jalankan 3 hal, masing-masing di terminal sendiri:
    docker compose up -d
    celery -A after:celery_app worker --loglevel=info --pool=solo
    uvicorn after:app --reload
"""
import time

from celery import Celery
from celery.result import AsyncResult
from fastapi import FastAPI

celery_app = Celery("demo", broker="redis://localhost:6379/0", backend="redis://localhost:6379/1")
celery_app.conf.task_track_started = True
app = FastAPI()

STATUS = {"PENDING": "pending", "STARTED": "running", "RETRY": "retrying",
          "SUCCESS": "done", "FAILURE": "failed"}


@celery_app.task
def generate_sales_report(month: str) -> dict:
    time.sleep(10)
    return {"month": month, "orders": 120, "revenue": 54_000_000}


@app.post("/reports/sales", status_code=202)
def create_sales_report(month: str):
    task = generate_sales_report.delay(month)
    return {"task_id": task.id, "status_url": f"/reports/{task.id}"}


@app.get("/reports/{task_id}")
def get_report(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": STATUS.get(result.state, result.state.lower()),
        "result": result.result if result.successful() else None,
        "error": str(result.result) if result.failed() else None,
    }
