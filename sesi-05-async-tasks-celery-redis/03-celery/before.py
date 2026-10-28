"""Celery - BEFORE (report dibuat dengan BackgroundTasks)

Response memang langsung keluar, tapi:
- report dibuat di proses API yang sama, CPU-nya dipakai bergantian dengan request lain
- server restart atau deploy di tengah proses = report hilang, tidak ada yang tahu
- tidak ada retry kalau gagal
- client tidak bisa mengecek report-nya sudah selesai atau belum

Jalankan: uvicorn before:app --reload
"""
import time

from fastapi import BackgroundTasks, FastAPI

app = FastAPI()


def generate_sales_report(month: str) -> dict:
    time.sleep(10)                # anggap: query order sebulan
    report = {"month": month, "orders": 120, "revenue": 54_000_000}
    print("[REPORT]", report)
    return report


@app.post("/reports/sales", status_code=202)
def create_sales_report(month: str,
                        background_tasks: BackgroundTasks):
    background_tasks.add_task(generate_sales_report, month)
    return {"message": "Report sedang dibuat"}   # cek hasilnya?
