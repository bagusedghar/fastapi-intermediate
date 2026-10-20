"""Value Object - BEFORE

Harga dan diskon cuma int biasa.
Tidak ada yang mencegah harga negatif, dan tidak jelas angka 10 itu
maksudnya 10 persen atau 10 rupiah.
"""


def apply_discount(subtotal: int, discount: int) -> int:
    return subtotal - discount


if __name__ == "__main__":
    print(apply_discount(100_000, 10))    # 99990, padahal maksudnya diskon 10%
    print(apply_discount(-50_000, 0))     # harga negatif lolos begitu saja
