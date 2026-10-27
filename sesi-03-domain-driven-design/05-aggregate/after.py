"""Aggregate - AFTER

Order adalah aggregate root. OrderLine hanya boleh diubah lewat Order.
- item ditambah lewat add_item(), yang mengecek qty dan status order
- total selalu dihitung dari item, jadi tidak mungkin basi
- dari luar, lines hanya bisa dibaca (tuple), tidak bisa di-append
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class OrderLine:
    product: str
    price: int
    qty: int

    @property
    def subtotal(self) -> int:
        return self.price * self.qty


class OrderCannotBeChanged(Exception):
    pass


class Order:
    def __init__(self, customer: str):
        self.customer = customer
        self.status = "pending"
        self._lines: list[OrderLine] = []

    @property
    def lines(self) -> tuple[OrderLine, ...]:
        return tuple(self._lines)

    @property
    def total(self) -> int:
        return sum(line.subtotal for line in self._lines)

    def add_item(self, product: str, price: int, qty: int) -> None:
        if self.status != "pending":
            raise OrderCannotBeChanged(
                "Item hanya bisa ditambah ke order pending"
            )
        if qty <= 0:
            raise ValueError("Qty harus lebih dari 0")
        self._lines.append(OrderLine(product, price, qty))

    def pay(self) -> None:
        if not self._lines:
            raise OrderCannotBeChanged(
                "Order kosong tidak bisa dibayar"
            )
        self.status = "paid"


if __name__ == "__main__":
    order = Order("budi@mail.com")
    order.add_item("Keyboard", 500_000, 2)
    print(order.total)              # 1000000, selalu sesuai item

    order.pay()
    try:
        order.add_item("Mouse", 100_000, 1)
    except OrderCannotBeChanged as e:
        print("Ditolak:", e)
