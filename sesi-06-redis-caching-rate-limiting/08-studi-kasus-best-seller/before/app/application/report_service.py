"""Application: use case report penjualan.

Dijalankan oleh worker Celery, bukan oleh request API, karena bisa lama kalau datanya banyak.
"""
from app.application.ports import UnitOfWork
from app.domain.order import OrderStatus


class ReportService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def sales_summary(self) -> dict:
        with self.uow:
            orders = self.uow.orders.list()

        paid = [o for o in orders if o.status == OrderStatus.PAID]
        return {
            "total_orders": len(orders),
            "paid_orders": len(paid),
            "cancelled_orders": sum(o.status == OrderStatus.CANCELLED for o in orders),
            "revenue": sum(o.total.amount for o in paid),
        }
