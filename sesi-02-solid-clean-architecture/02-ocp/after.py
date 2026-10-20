"""OCP (Open/Closed) - AFTER

"Open for extension, closed for modification."
Kurir baru = class baru + daftarkan di COURIERS. shipping_cost() tidak disentuh.
"""


class RegularCourier:
    def cost(self, weight_kg: int) -> int:
        return 10_000 * weight_kg


class ExpressCourier:
    def cost(self, weight_kg: int) -> int:
        return 20_000 * weight_kg


class SameDayCourier:  # kurir baru
    def cost(self, weight_kg: int) -> int:
        return 35_000 + 15_000 * weight_kg


COURIERS = {
    "regular": RegularCourier(),
    "express": ExpressCourier(),
    "same_day": SameDayCourier(),
}


def shipping_cost(courier: str, weight_kg: int) -> int:
    if courier not in COURIERS:
        raise ValueError(f"Kurir tidak dikenal: {courier}")
    return COURIERS[courier].cost(weight_kg)


if __name__ == "__main__":
    for name in COURIERS:
        print(name, shipping_cost(name, 2))
