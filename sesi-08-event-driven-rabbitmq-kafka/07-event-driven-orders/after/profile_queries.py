"""Ukur performa query aplikasi: waktu dan jumlah query ke database.

Jumlah query dihitung lewat event SQLAlchemy "before_cursor_execute",
yang terpanggil setiap kali ada SQL dikirim ke database.

Jalankan seed.py dulu, lalu dari folder before/ dan after/: python profile_queries.py
Bandingkan hasil keduanya.
"""
import os

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://app:app@localhost:5432/orders")
os.environ.setdefault("QUERY_DELAY", "0")         # matikan simulasi query lambat dari Sesi 6

import statistics  # noqa: E402
import time  # noqa: E402

from sqlalchemy import event  # noqa: E402

from app.application.report_service import ReportService  # noqa: E402
from app.infrastructure.database import get_session_factory  # noqa: E402
from app.infrastructure.unit_of_work import SqlAlchemyUnitOfWork  # noqa: E402

session_factory = get_session_factory()
queries = 0


@event.listens_for(session_factory.kw["bind"], "before_cursor_execute")
def count_query(*args):
    global queries
    queries += 1


def measure(fn) -> tuple[float, int]:
    global queries
    queries = 0
    start = time.perf_counter()
    fn()
    return (time.perf_counter() - start) * 1000, queries


def order_detail() -> None:
    uow = SqlAlchemyUnitOfWork(session_factory)
    with uow:
        uow.orders.get(12345)


if __name__ == "__main__":
    report_ms, report_queries = measure(ReportService(SqlAlchemyUnitOfWork(session_factory)).sales_summary)
    details = [measure(order_detail) for _ in range(50)]

    print(f"Report penjualan       : {report_ms:8.1f} ms, {report_queries} query")
    print(f"Detail order (median)  : {statistics.median(ms for ms, _ in details):8.1f} ms, {details[0][1]} query")
