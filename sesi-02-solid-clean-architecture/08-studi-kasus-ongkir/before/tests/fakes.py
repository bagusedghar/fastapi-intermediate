"""Fake adapter untuk test. Bentuknya sama dengan port, isinya cuma list/dict."""
from dataclasses import replace

from app.domain.order import Order


class FakeOrderRepository:
    def __init__(self):
        self.rows: dict[int, Order] = {}

    def add(self, order: Order) -> Order:
        saved = replace(order, id=len(self.rows) + 1)
        self.rows[saved.id] = saved
        return saved

    def get(self, order_id: int) -> Order | None:
        return self.rows.get(order_id)


class FakeNotifier:
    def __init__(self):
        self.sent: list[tuple[str, str]] = []

    def send(self, to: str, message: str) -> None:
        self.sent.append((to, message))
