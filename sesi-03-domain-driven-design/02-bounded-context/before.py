"""Bounded Context - BEFORE

Satu class Customer dipakai semua bagian aplikasi.
Bagian penjualan (Sales) butuh tipe customer untuk diskon,
bagian pengiriman (Shipping) butuh alamat dan nomor HP.
Hasilnya class makin gemuk, dan setiap perubahan untuk satu tim
berisiko merusak kode tim lain.
"""
from dataclasses import dataclass


@dataclass
class Customer:
    email: str
    name: str
    customer_type: str      # dipakai Sales
    loyalty_points: int     # dipakai Sales
    address: str            # dipakai Shipping
    phone: str              # dipakai Shipping
    courier: str            # dipakai Shipping


def discount_percent(customer: Customer) -> int:
    rates = {"regular": 0, "member": 5, "vip": 10}
    return rates[customer.customer_type]


def shipping_label(customer: Customer) -> str:
    c = customer
    return f"{c.name} | {c.address} | {c.phone}"


if __name__ == "__main__":
    budi = Customer(
        "budi@mail.com", "Budi", "vip", 120,
        "Jl. Merdeka 1, Bandung", "0812-1111", "express",
    )
    print(discount_percent(budi))
    print(shipping_label(budi))
