"""Bounded Context - AFTER

Aplikasi dibagi per context. Setiap context punya model sendiri
yang hanya berisi data yang ia butuhkan.
Orang yang sama (Budi) disebut "Customer" di Sales dan "Recipient" di Shipping.
Di project sungguhan, setiap context biasanya jadi folder atau module sendiri.
"""
from dataclasses import dataclass


# ===================== Sales context =====================
@dataclass
class Customer:
    email: str
    customer_type: str
    loyalty_points: int = 0


def discount_percent(customer: Customer) -> int:
    return {"regular": 0, "member": 5, "vip": 10}[customer.customer_type]


# ===================== Shipping context =====================
@dataclass
class Recipient:
    name: str
    address: str
    phone: str


@dataclass
class Shipment:
    order_id: int          # yang dibagi antar context cukup id-nya
    recipient: Recipient
    courier: str


def shipping_label(shipment: Shipment) -> str:
    r = shipment.recipient
    return f"Order #{shipment.order_id} | {r.name} | {r.address} | {r.phone}"


if __name__ == "__main__":
    print(discount_percent(Customer("budi@mail.com", "vip")))
    print(shipping_label(Shipment(1, Recipient("Budi", "Jl. Merdeka 1, Bandung", "0812-1111"), "express")))
