"""Service Layer - AFTER

Business logic dipindah ke OrderService. Service tidak meng-import FastAPI,
jadi bisa dipanggil dari mana saja dan dites tanpa HTTP.
Endpoint tinggal menerjemahkan: request -> service -> response / HTTP error.

Jalankan: uvicorn after:app --reload
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# ---------- service: murni Python, tanpa FastAPI ----------
class BusinessError(Exception):
    pass


class OrderService:
    def __init__(self):
        self.orders: dict[int, dict] = {}

    def place_order(self, customer: str, subtotal: int) -> dict:
        if subtotal < 10_000:
            raise BusinessError("Minimal order Rp10.000")
        total = subtotal - subtotal * 5 // 100
        order = {"id": len(self.orders) + 1, "customer": customer, "total": total}
        self.orders[order["id"]] = order
        print(f"[EMAIL] ke {customer}: Order #{order['id']} berhasil dibuat")
        return order


# ---------- route: simple, hanya menghandle HTTP ----------
app = FastAPI()
service = OrderService()


class OrderIn(BaseModel):
    customer: str
    subtotal: int


@app.post("/orders", status_code=201)
def create_order(payload: OrderIn):
    try:
        return service.place_order(payload.customer, payload.subtotal)
    except BusinessError as e:
        raise HTTPException(400, str(e))


if __name__ == "__main__":
    # service bisa dipakai tanpa server sama sekali
    print(OrderService().place_order("budi@mail.com", 200_000))
