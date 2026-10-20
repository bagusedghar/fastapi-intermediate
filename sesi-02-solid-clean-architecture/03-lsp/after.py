"""LSP (Liskov Substitution) - AFTER

Semua subclass mengikuti kontrak yang sama: kembalikan besar potongan, 0 sampai subtotal.
Kontraknya juga dicek oleh satu test yang dijalankan untuk SEMUA subclass,
jadi kalau ada subclass baru yang melanggar, langsung ketahuan.
"""


class Discount:
    def discount(self, subtotal: int) -> int:
        """Kembalikan besar potongan (0 sampai subtotal)."""
        return 0


class MemberDiscount(Discount):
    def discount(self, subtotal: int) -> int:
        return subtotal * 5 // 100


class VoucherDiscount(Discount):
    def __init__(self, amount: int = 50_000):
        self.amount = amount

    def discount(self, subtotal: int) -> int:
        return min(self.amount, subtotal)  # potongan, tidak lebih dari subtotal


def calculate_total(subtotal: int, rule: Discount) -> int:
    return subtotal - rule.discount(subtotal)


def check_contract(rule: Discount) -> None:
    for subtotal in (0, 30_000, 200_000):
        assert 0 <= rule.discount(subtotal) <= subtotal, type(rule).__name__


if __name__ == "__main__":
    for rule in (Discount(), MemberDiscount(), VoucherDiscount()):
        check_contract(rule)
        print(type(rule).__name__, calculate_total(200_000, rule))
