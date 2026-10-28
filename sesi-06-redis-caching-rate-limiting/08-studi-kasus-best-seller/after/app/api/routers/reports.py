"""API: endpoint report.

Report dibuat oleh worker. API cuma memulai job (202 Accepted) dan menampilkan status-nya.
"""
from fastapi import APIRouter, Depends

from app.api.rate_limit import rate_limit
from app.api.schemas import ErrorOut, JobOut, ReportStatusOut
from app.worker.jobs import get_job_status, start_sales_report

router = APIRouter(prefix="/reports", tags=["reports"], dependencies=[Depends(rate_limit)],
                   responses={429: {"model": ErrorOut, "description": "Terlalu banyak request (rate limit)"}})


@router.post("/sales", status_code=202, response_model=JobOut, summary="Buat report penjualan (background job)")
def create_sales_report():
    task_id = start_sales_report()
    return JobOut(task_id=task_id, status="pending", status_url=f"/reports/{task_id}")


@router.get("/{task_id}", response_model=ReportStatusOut, summary="Cek status dan hasil report")
def get_sales_report(task_id: str):
    return get_job_status(task_id)
