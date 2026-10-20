"""ISP (Interface Segregation) - AFTER

Interface dipecah sesuai kebutuhan pemakainya.
ReportService hanya bergantung pada OrderReader, jadi fake-nya cukup satu method.
Repository asli tetap boleh mengimplementasikan keduanya.
"""
from typing import Protocol


class OrderReader(Protocol):
    def get(self, order_id: int) -> dict | None: ...
    def list_all(self) -> list[dict]: ...


class OrderWriter(Protocol):
    def add(self, order: dict) -> dict: ...
    def update_status(self, order_id: int, status: str) -> None: ...


class ReportService:
    def __init__(self, reader: OrderReader):
        self.reader = reader

    def total_revenue(self) -> int:
        return sum(o["total"] for o in self.reader.list_all())


class FakeReader:
    def list_all(self):
        return [{"total": 100_000}, {"total": 250_000}]


if __name__ == "__main__":
    print(ReportService(FakeReader()).total_revenue())
