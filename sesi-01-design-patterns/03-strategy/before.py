"""Strategy - BEFORE

Semua aturan diskon ada di satu function. Setiap ada tipe customer baru,
function ini harus diedit dan makin panjang. Mengetes satu aturan juga
berarti ikut menjalankan semua aturan lain.
"""


def calculate_total(subtotal: int, customer_type: str) -> int:
    if customer_type == "regular":
        discount = 0
    elif customer_type == "member":
        discount = subtotal * 5 // 100
    elif customer_type == "vip":
        discount = subtotal * 10 // 100
    # elif customer_type == "student": ... <- nambah di sini terus
    else:
        raise ValueError(f"Tipe customer tidak dikenal: {customer_type}")
    return subtotal - discount


if __name__ == "__main__":
    for t in ("regular", "member", "vip"):
        print(t, calculate_total(1_000_000, t))
