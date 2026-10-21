"""Celery - AFTER

API hanya menaruh job ke antrean (broker = Redis), lalu langsung menjawab.
Worker Celery (proses terpisah) mengambil job dari antrean dan mengerjakannya.
Hasilnya disimpan di result backend (Redis juga).

Jalankan 3 hal, masing-masing di terminal sendiri:
    docker compose up -d                                   # Redis (dari folder sesi-05)
    celery -A after:celery_app worker --loglevel=info --pool=solo
    uvicorn after:app --reload

`--pool=solo` diperlukan di Windows. Di Linux/Mac boleh dihapus.
"""
import time

from celery import Celery
from fastapi import FastAPI

celery_app = Celery("demo", broker="redis://localhost:6379/0", backend="redis://localhost:6379/1")
app = FastAPI()


@celery_app.task
def generate_sales_report(month: str) -> dict:
    time.sleep(10)                    # dikerjakan oleh worker, bukan oleh API
    return {"month": month, "orders": 120, "revenue": 54_000_000}


@app.post("/reports/sales", status_code=202)
def create_sales_report(month: str):
    task = generate_sales_report.delay(month)                 # masuk antrean, tidak menunggu
    return {"task_id": task.id}
