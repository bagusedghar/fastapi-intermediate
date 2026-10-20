"""Service Layer: business logic order. Tidak import FastAPI maupun sqlite3."""
from discounts import get_discount
from notifiers import Notifier
from repository import OrderRepository


class OrderNotFound(Exception):
    pass


class OrderService:
    def __init__(self, repo: OrderRepository, notifier: Notifier):
        self.repo = repo
        self.notifier = notifier

    def place_order(self, customer: str, customer_type: str, items: list[dict]) -> dict:
        subtotal = sum(i["price"] * i["qty"] for i in items)
        total = subtotal - get_discount(customer_type).discount(subtotal)
        order = self.repo.add({
            "customer": customer,
            "customer_type": customer_type,
            "subtotal": subtotal,
            "total": total,
        })
        self.notifier.send(customer, f"Order #{order['id']} total Rp{total:,}")
        return order

    def get_order(self, order_id: int) -> dict:
        order = self.repo.get(order_id)
        if order is None:
            raise OrderNotFound("Order tidak ditemukan")
        return order
