"""Domain: aturan ongkos kirim (Strategy). Murni Python, tidak tahu soal database atau HTTP.

Satu class per cara kirim. Kurir baru = class/objek baru di COURIERS, OrderService tidak diubah.
Gratis ongkir kalau belanja (setelah diskon) minimal FREE_SHIPPING_MIN.
"""
from typing import Protocol

FREE_SHIPPING_MIN = 500_000


class ShippingStrategy(Protocol):
    def cost(self, amount: int) -> int: ...


class Pickup:
    def cost(self, amount: int) -> int:
        return 0


class FlatRateCourier:
    def __init__(self, fee: int):
        self.fee = fee

    def cost(self, amount: int) -> int:
        if amount >= FREE_SHIPPING_MIN:
            return 0
        return self.fee


COURIERS: dict[str, ShippingStrategy] = {
    "pickup": Pickup(),
    "jne": FlatRateCourier(15_000),
    "sicepat": FlatRateCourier(12_000),
}


class UnknownCourier(Exception):
    pass


def get_courier(courier: str) -> ShippingStrategy:
    if courier not in COURIERS:
        raise UnknownCourier("Kurir tidak dikenal")
    return COURIERS[courier]
