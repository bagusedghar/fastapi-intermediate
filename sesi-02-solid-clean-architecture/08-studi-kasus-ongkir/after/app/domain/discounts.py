"""Domain: aturan diskon (Strategy). Murni Python, tidak tahu soal database atau HTTP."""
from typing import Protocol


class DiscountStrategy(Protocol):
    def discount(self, subtotal: int) -> int: ...


class NoDiscount:
    def discount(self, subtotal: int) -> int:
        return 0


class PercentDiscount:
    def __init__(self, percent: int):
        self.percent = percent

    def discount(self, subtotal: int) -> int:
        return subtotal * self.percent // 100


DISCOUNTS: dict[str, DiscountStrategy] = {
    "regular": NoDiscount(),
    "member": PercentDiscount(5),
    "vip": PercentDiscount(10),
}


class UnknownCustomerType(Exception):
    pass


def get_discount(customer_type: str) -> DiscountStrategy:
    if customer_type not in DISCOUNTS:
        raise UnknownCustomerType("Tipe customer tidak dikenal")
    return DISCOUNTS[customer_type]
