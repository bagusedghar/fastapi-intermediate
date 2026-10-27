"""Domain Service - AFTER

DiscountPolicy adalah domain service: business logic yang melibatkan
Customer dan Order sekaligus, jadi tidak pas ditaruh di salah satunya.
- DiscountPolicy menghitung besar diskon
- Order cukup menerima diskon dan menjaga aturannya sendiri (diskon tidak boleh melebihi subtotal)
- tidak ada database atau HTTP di sini, jadi tetap bagian dari domain
"""
from datetime import date


class Customer:
    def __init__(self, email: str, customer_type: str):
        self.email = email
        self.customer_type = customer_type


class Order:
    def __init__(self, customer_email: str, subtotal: int):
        self.customer_email = customer_email
        self.subtotal = subtotal
        self.discount = 0

    def apply_discount(self, amount: int) -> None:
        if amount > self.subtotal:
            raise ValueError(
                "Diskon tidak boleh melebihi subtotal"
            )
        self.discount = amount

    @property
    def total(self) -> int:
        return self.subtotal - self.discount


class DiscountPolicy:
    RATES = {"regular": 0, "member": 5, "vip": 10}

    def discount_for(
        self, customer: Customer, order: Order, today: date
    ) -> int:
        percent = self.RATES[customer.customer_type]
        if today.month == 12:            # promo akhir tahun
            percent += 5
        return order.subtotal * percent // 100


if __name__ == "__main__":
    budi = Customer("budi@mail.com", "vip")
    order = Order(budi.email, 1_000_000)
    today = date(2026, 12, 1)
    discount = DiscountPolicy().discount_for(budi, order, today)
    order.apply_discount(discount)
    print(order.total)   # 850000
