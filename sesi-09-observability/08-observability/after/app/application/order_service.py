"""Application: use case order.

Setiap use case berjalan dalam satu Unit of Work (satu transaksi):
- place_order  : kurangi stok semua item + simpan order
- cancel_order : kembalikan stok semua item + ubah status
- list_orders  : riwayat order customer per halaman (keyset pagination)
Kalau satu langkah gagal, semua langkah dibatalkan (rollback).
Setelah commit, use case mengumumkan event (order.placed, order.paid, order.cancelled).
Event tidak dikirim kalau transaksinya gagal, jadi tidak ada notifikasi untuk order yang batal tersimpan.
"""
from app.application.errors import OrderNotFound, ProductNotFound
from app.application.events import ORDER_CANCELLED, ORDER_PAID, ORDER_PLACED, order_event
from app.application.ports import EventPublisher, UnitOfWork
from app.domain.discount_policy import DiscountPolicy
from app.domain.order import Order
from app.domain.product import Product


class OrderService:
    def __init__(self, uow: UnitOfWork, events: EventPublisher):
        self.uow = uow
        self.events = events
        self.discount_policy = DiscountPolicy()

    def place_order(self, customer: str, customer_type: str, items: list[dict]) -> Order:
        with self.uow:
            order = Order(customer, customer_type)
            for item in items:
                product = self._get_product(item["product_id"])
                product.reserve(item["qty"])
                order.add_item(product.id, product.name, product.price, item["qty"])
                self.uow.products.save(product)
            order.apply_discount(self.discount_policy.discount_for(order))
            self.uow.orders.add(order)
            self.uow.commit()

        self.events.publish(order_event(ORDER_PLACED, order))
        return order

    def pay_order(self, order_id: int) -> Order:
        with self.uow:
            order = self._get_order(order_id)
            order.pay()
            self.uow.orders.save(order)
            self.uow.commit()

        self.events.publish(order_event(ORDER_PAID, order))
        return order

    def cancel_order(self, order_id: int) -> Order:
        with self.uow:
            order = self._get_order(order_id)
            order.cancel()
            for line in order.lines:
                product = self._get_product(line.product_id)
                product.release(line.qty)
                self.uow.products.save(product)
            self.uow.orders.save(order)
            self.uow.commit()

        self.events.publish(order_event(ORDER_CANCELLED, order))
        return order

    def list_orders(self, customer: str, limit: int = 20, after: int | None = None) -> list[Order]:
        with self.uow:
            return self.uow.orders.list_for_customer(customer, limit, after)

    def get_order(self, order_id: int) -> Order:
        with self.uow:
            return self._get_order(order_id)

    def _get_order(self, order_id: int) -> Order:
        order = self.uow.orders.get(order_id)
        if order is None:
            raise OrderNotFound(f"Order #{order_id} tidak ditemukan")
        return order

    def _get_product(self, product_id: int) -> Product:
        product = self.uow.products.get(product_id)
        if product is None:
            raise ProductNotFound(f"Product #{product_id} tidak ditemukan")
        return product
