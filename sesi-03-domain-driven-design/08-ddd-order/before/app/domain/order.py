"""Domain: bentuk data order. Tidak import apa pun dari layer lain."""
from dataclasses import dataclass


@dataclass
class Order:
    customer: str
    customer_type: str
    subtotal: int
    total: int
    id: int | None = None
