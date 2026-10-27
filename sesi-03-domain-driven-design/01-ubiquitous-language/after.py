"""Ubiquitous Language - AFTER

Nama di kode sama dengan istilah yang dipakai tim bisnis:
order, customer, total, pending, paid, cancelled, pay, cancel.
Kode bisa dibaca bareng tim bisnis tanpa perlu diterjemahkan.
"""
from dataclasses import dataclass
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"


@dataclass
class Order:
    customer: str
    total: int
    status: OrderStatus = OrderStatus.PENDING


class OrderCannotBeChanged(Exception):
    pass


def pay_order(order: Order) -> None:
    if order.status != OrderStatus.PENDING:
        raise OrderCannotBeChanged(
            "Hanya order pending yang bisa dibayar"
        )
    order.status = OrderStatus.PAID


def cancel_order(order: Order) -> None:
    if order.status != OrderStatus.PENDING:
        raise OrderCannotBeChanged(
            "Hanya order pending yang bisa dibatalkan"
        )
    order.status = OrderStatus.CANCELLED


if __name__ == "__main__":
    order = Order(customer="budi@mail.com", total=200_000)
    pay_order(order)
    print(order.status.value)  # paid
