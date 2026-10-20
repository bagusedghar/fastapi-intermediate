"""Domain Service - BEFORE

Aturan diskon dimasukkan ke dalam Order.
Padahal diskon butuh data Customer (tipe member) dan sering berubah karena promo.
Order jadi harus tahu soal tipe customer dan kalender promo,
dan setiap ada promo baru, entity Order ikut diedit.
"""
from datetime import date


class Customer:
    def __init__(self, email: str, customer_type: str):
        self.email = email
        self.customer_type = customer_type


class Order:
    def __init__(self, customer: Customer, subtotal: int):
        self.customer = customer
        self.subtotal = subtotal

    def total(self, today: date) -> int:
        percent = {"regular": 0, "member": 5, "vip": 10}[self.customer.customer_type]
        if today.month == 12:            # promo akhir tahun
            percent += 5
        return self.subtotal - self.subtotal * percent // 100


if __name__ == "__main__":
    order = Order(Customer("budi@mail.com", "vip"), 1_000_000)
    print(order.total(date(2026, 12, 1)))   # 850000
