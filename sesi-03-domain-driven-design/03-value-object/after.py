"""Value Object - AFTER

Money adalah value object:
- dikenali dari nilainya, bukan dari id (Money(100_000) == Money(100_000))
- immutable, tidak bisa diubah setelah dibuat (frozen=True)
- memvalidasi dirinya sendiri, jadi tidak mungkin ada Money negatif
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    amount: int

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Money tidak boleh negatif")

    def __add__(self, other: "Money") -> "Money":
        return Money(self.amount + other.amount)

    def __sub__(self, other: "Money") -> "Money":
        return Money(self.amount - other.amount)

    def times(self, qty: int) -> "Money":
        return Money(self.amount * qty)

    def percent(self, value: int) -> "Money":
        return Money(self.amount * value // 100)


def apply_discount(subtotal: Money, discount: Money) -> Money:
    return subtotal - discount


if __name__ == "__main__":
    subtotal = Money(100_000)
    print(apply_discount(subtotal, subtotal.percent(10)))  # 90000
    print(apply_discount(subtotal, Money(10)))  # potongan Rp10
    print(Money(100_000) == Money(100_000))  # True, nilainya sama

    try:
        Money(-50_000)
    except ValueError as e:
        print("Ditolak:", e)
