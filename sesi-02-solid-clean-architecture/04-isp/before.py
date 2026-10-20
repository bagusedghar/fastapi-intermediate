"""ISP (Interface Segregation) - BEFORE

Satu interface besar berisi semua operasi order.
ReportService cuma butuh list_all(), tapi fake untuk test-nya
tetap wajib mengisi semua method, padahal tidak dipakai.
"""
from abc import ABC, abstractmethod


class OrderRepository(ABC):
    @abstractmethod
    def add(self, order: dict) -> dict: ...

    @abstractmethod
    def get(self, order_id: int) -> dict | None: ...

    @abstractmethod
    def list_all(self) -> list[dict]: ...

    @abstractmethod
    def update_status(self, order_id: int, status: str) -> None: ...

    @abstractmethod
    def delete(self, order_id: int) -> None: ...


class ReportService:
    def __init__(self, repo: OrderRepository):
        self.repo = repo

    def total_revenue(self) -> int:
        return sum(o["total"] for o in self.repo.list_all())


class FakeRepoForReport(OrderRepository):
    def list_all(self):
        return [{"total": 100_000}, {"total": 250_000}]

    # method di bawah tidak dipakai, tapi wajib ditulis
    def add(self, order):
        raise NotImplementedError

    def get(self, order_id):
        raise NotImplementedError

    def update_status(self, order_id, status):
        raise NotImplementedError

    def delete(self, order_id):
        raise NotImplementedError


if __name__ == "__main__":
    print(ReportService(FakeRepoForReport()).total_revenue())
