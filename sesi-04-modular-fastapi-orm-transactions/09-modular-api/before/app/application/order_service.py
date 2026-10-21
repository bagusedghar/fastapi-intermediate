"""Application: use case order.

Setiap method adalah satu use case. Polanya selalu sama:
ambil / buat aggregate -> panggil method domain -> simpan -> efek samping (notifikasi).
Business logic-nya sendiri ada di domain, bukan di sini.
"""
from app.application.ports import Notifier, OrderRepository
from app.domain.discount_policy import DiscountPolicy
from app.domain.money import Money
from app.domain.order import Order


class OrderNotFound(Exception):
    pass


class OrderService:
    def __init__(self, repo: OrderRepository, notifier: Notifier):
        self.repo = repo
        self.notifier = notifier
        self.discount_policy = DiscountPolicy()

    def place_order(self, customer: str, customer_type: str, items: list[dict]) -> Order:
        order = Order(customer, customer_type)
        for item in items:
            order.add_item(item["name"], Money(item["price"]), item["qty"])
        order.apply_discount(self.discount_policy.discount_for(order))

        order = self.repo.add(order)
        self.notifier.send(customer, f"Order #{order.id} total Rp{order.total.amount:,}")
        return order

    def pay_order(self, order_id: int) -> Order:
        order = self.get_order(order_id)
        order.pay()
        self.repo.save(order)
        self.notifier.send(order.customer, f"Order #{order.id} sudah dibayar")
        return order

    def cancel_order(self, order_id: int) -> Order:
        order = self.get_order(order_id)
        order.cancel()
        self.repo.save(order)
        self.notifier.send(order.customer, f"Order #{order.id} dibatalkan")
        return order

    def get_order(self, order_id: int) -> Order:
        order = self.repo.get(order_id)
        if order is None:
            raise OrderNotFound("Order tidak ditemukan")
        return order
