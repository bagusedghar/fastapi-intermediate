"""Aggregate - BEFORE

Order dan item-nya bisa diubah langsung dari luar.
Akibatnya total lupa diupdate, qty bisa negatif,
dan item tetap bisa ditambah walaupun order sudah dibayar.
"""
from dataclasses import dataclass, field


@dataclass
class OrderLine:
    product: str
    price: int
    qty: int


@dataclass
class Order:
    customer: str
    lines: list[OrderLine] = field(default_factory=list)
    total: int = 0
    status: str = "pending"


if __name__ == "__main__":
    order = Order("budi@mail.com")
    order.lines.append(OrderLine("Keyboard", 500_000, 2))
    print(order.total)  # 0, total lupa dihitung

    order.status = "paid"
    # qty negatif, setelah dibayar pula
    order.lines.append(OrderLine("Mouse", 100_000, -3))
    print(len(order.lines), order.status)
