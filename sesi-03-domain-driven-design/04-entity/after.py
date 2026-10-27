"""Entity - AFTER

Order adalah entity:
- punya identitas (id). Dua order dianggap sama kalau id-nya sama, walaupun statusnya berubah.
- punya lifecycle: pending -> paid / cancelled.
- perubahan status hanya lewat method pay() dan cancel(), yang menjaga business logic-nya.
"""
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"


class OrderCannotBeChanged(Exception):
    pass


class Order:
    def __init__(self, id: int, customer: str, total: int):
        self.id = id
        self.customer = customer
        self.total = total
        self.status = OrderStatus.PENDING

    def pay(self) -> None:
        self._ensure_pending("dibayar")
        self.status = OrderStatus.PAID

    def cancel(self) -> None:
        self._ensure_pending("dibatalkan")
        self.status = OrderStatus.CANCELLED

    def _ensure_pending(self, action: str) -> None:
        if self.status != OrderStatus.PENDING:
            raise OrderCannotBeChanged(
                f"Order {self.status.value} tidak bisa {action}"
            )

    def __eq__(self, other) -> bool:
        return isinstance(other, Order) and self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


if __name__ == "__main__":
    order = Order(1, "budi@mail.com", 200_000)
    order.pay()
    try:
        order.cancel()
    except OrderCannotBeChanged as e:
        print("Ditolak:", e)

    # True: id-nya sama, walaupun statusnya berbeda
    print(order == Order(1, "budi@mail.com", 200_000))
