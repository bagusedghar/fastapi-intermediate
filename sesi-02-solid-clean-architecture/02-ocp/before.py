"""OCP (Open/Closed) - BEFORE

Ongkir dihitung dengan if/elif. Setiap ada kurir baru, function ini harus dibuka dan diedit.
Kode yang sudah jalan dan sudah dites jadi ikut berisiko rusak.
"""


def shipping_cost(courier: str, weight_kg: int) -> int:
    if courier == "regular":
        return 10_000 * weight_kg
    elif courier == "express":
        return 20_000 * weight_kg
    # elif courier == "same_day": ...  <- edit lagi di sini
    raise ValueError(f"Kurir tidak dikenal: {courier}")


if __name__ == "__main__":
    print(shipping_cost("regular", 2))
    print(shipping_cost("express", 2))
