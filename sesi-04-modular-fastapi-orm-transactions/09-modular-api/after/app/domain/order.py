"""Domain: aggregate Order.

Order adalah entity sekaligus aggregate root.
OrderLine (item) hanya bisa ditambah lewat Order, dan semua business logic order dijaga di sini.
Product cukup dirujuk lewat product_id, bukan object Product-nya.
"""
from dataclasses import dataclass
from enum import Enum

from app.domain.errors import OrderCannotBeChanged
from app.domain.money import Money


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class OrderLine:
    product_id: int
    product: str
    price: Money
    qty: int

    @property
    def subtotal(self) -> Money:
        return self.price.times(self.qty)


class Order:
    def __init__(self, customer: str, customer_type: str, *, id: int | None = None,
                 status: OrderStatus = OrderStatus.PENDING,
                 lines: list[OrderLine] | None = None, discount: Money = Money(0)):
        self.id = id
        self.customer = customer
        self.customer_type = customer_type
        self.status = status
        self.discount = discount
        self._lines = list(lines or [])

    @property
    def lines(self) -> tuple[OrderLine, ...]:
        return tuple(self._lines)

    @property
    def subtotal(self) -> Money:
        return sum((line.subtotal for line in self._lines), Money(0))

    @property
    def total(self) -> Money:
        return self.subtotal - self.discount

    def add_item(self, product_id: int, product: str, price: Money, qty: int) -> None:
        self._ensure_pending("diubah")
        if qty <= 0:
            raise ValueError("Qty harus lebih dari 0")
        self._lines.append(OrderLine(product_id, product, price, qty))

    def apply_discount(self, amount: Money) -> None:
        self._ensure_pending("diubah")
        if amount.amount > self.subtotal.amount:
            raise ValueError("Diskon tidak boleh melebihi subtotal")
        self.discount = amount

    def pay(self) -> None:
        self._ensure_pending("dibayar")
        if not self._lines:
            raise OrderCannotBeChanged("Order kosong tidak bisa dibayar")
        self.status = OrderStatus.PAID

    def cancel(self) -> None:
        self._ensure_pending("dibatalkan")
        self.status = OrderStatus.CANCELLED

    def _ensure_pending(self, action: str) -> None:
        if self.status != OrderStatus.PENDING:
            raise OrderCannotBeChanged(f"Order {self.status.value} tidak bisa {action}")

    def __eq__(self, other) -> bool:
        return isinstance(other, Order) and self.id is not None and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
