"""Strategy - AFTER

Setiap aturan diskon jadi class sendiri dengan method yang sama: discount(subtotal).
calculate_total() tidak peduli aturan mana yang dipakai, yang penting punya method discount().
Tambah aturan baru = tambah class baru, calculate_total() tidak diubah.
"""
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


class StudentDiscount:  # aturan baru: 15%, maksimal Rp75.000
    def discount(self, subtotal: int) -> int:
        return min(subtotal * 15 // 100, 75_000)


DISCOUNTS = {
    "regular": NoDiscount(),
    "member": PercentDiscount(5),
    "vip": PercentDiscount(10),
    "student": StudentDiscount(),
}


def calculate_total(subtotal: int, strategy: DiscountStrategy) -> int:
    return subtotal - strategy.discount(subtotal)


if __name__ == "__main__":
    for t, strategy in DISCOUNTS.items():
        print(t, calculate_total(1_000_000, strategy))
