"""Application: use case order. Hanya bergantung pada domain dan ports."""
from app.application.ports import Notifier, OrderRepository
from app.domain.discounts import get_discount
from app.domain.order import Order


class OrderNotFound(Exception):
    pass


class OrderService:
    def __init__(self, repo: OrderRepository, notifier: Notifier):
        self.repo = repo
        self.notifier = notifier

    def place_order(self, customer: str, customer_type: str, items: list[dict]) -> Order:
        subtotal = sum(i["price"] * i["qty"] for i in items)
        total = subtotal - get_discount(customer_type).discount(subtotal)
        order = self.repo.add(Order(customer, customer_type, subtotal, total))
        self.notifier.send(customer, f"Order #{order.id} total Rp{total:,}")
        return order

    def get_order(self, order_id: int) -> Order:
        order = self.repo.get(order_id)
        if order is None:
            raise OrderNotFound("Order tidak ditemukan")
        return order
