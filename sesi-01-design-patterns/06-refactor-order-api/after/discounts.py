"""Strategy: satu class per aturan diskon. get_discount() memilih strategy dari tipe customer."""
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


def get_discount(customer_type: str) -> DiscountStrategy:
    if customer_type not in DISCOUNTS:
        raise ValueError("Tipe customer tidak dikenal")
    return DISCOUNTS[customer_type]
