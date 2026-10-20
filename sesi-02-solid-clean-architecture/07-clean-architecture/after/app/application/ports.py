"""Application: ports = interface yang dibutuhkan use case.
Implementasinya (adapter) ada di layer infrastructure.
"""
from typing import Protocol

from app.domain.order import Order


class OrderRepository(Protocol):
    def add(self, order: Order) -> Order: ...
    def get(self, order_id: int) -> Order | None: ...


class Notifier(Protocol):
    def send(self, to: str, message: str) -> None: ...
