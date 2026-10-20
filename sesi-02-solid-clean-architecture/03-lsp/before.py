"""LSP (Liskov Substitution) - BEFORE

Kontrak Discount: discount(subtotal) mengembalikan BESAR POTONGAN.
VoucherDiscount malah mengembalikan HARGA SETELAH DISKON.
Kodenya tidak error, tapi total jadi salah. Subclass tidak bisa menggantikan parent-nya.
"""


class Discount:
    def discount(self, subtotal: int) -> int:
        """Kembalikan besar potongan (0 sampai subtotal)."""
        return 0


class MemberDiscount(Discount):
    def discount(self, subtotal: int) -> int:
        return subtotal * 5 // 100


class VoucherDiscount(Discount):
    def discount(self, subtotal: int) -> int:
        return subtotal - 50_000  # salah: ini harga akhir, bukan potongan


def calculate_total(subtotal: int, rule: Discount) -> int:
    return subtotal - rule.discount(subtotal)


if __name__ == "__main__":
    print("member :", calculate_total(200_000, MemberDiscount()))   # 190000, benar
    print("voucher:", calculate_total(200_000, VoucherDiscount()))  # 50000, harusnya 150000
