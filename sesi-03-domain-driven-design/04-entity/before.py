"""Entity - BEFORE

Order cuma wadah data. Status bisa diubah dari mana saja,
jadi order yang sudah dibayar tetap bisa "dibatalkan".
Selain itu, dataclass membandingkan semua field: order #1 yang sama,
setelah statusnya berubah, dianggap order yang berbeda.
"""
from dataclasses import dataclass, replace


@dataclass
class Order:
    id: int
    customer: str
    total: int
    status: str = "pending"


if __name__ == "__main__":
    order = Order(1, "budi@mail.com", 200_000)
    order.status = "paid"
    order.status = "cancelled"  # padahal sudah dibayar
    print(order.status)

    before_paid = Order(1, "budi@mail.com", 200_000)
    after_paid = replace(before_paid, status="paid")
    print(before_paid == after_paid)  # False, padahal order #1
