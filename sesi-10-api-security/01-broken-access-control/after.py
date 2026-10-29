"""Broken Access Control - AFTER (setiap akses dicek terhadap pemiliknya)

Setelah order ditemukan, endpoint mengecek: apakah user ini pemilik order, atau admin?
Jika bukan, jawabannya 404, sama seperti order yang tidak ada.
Sengaja 404, bukan 403: 403 memberi tahu penyerang bahwa order dengan id itu ada.

Jalankan: python after.py
"""
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.testclient import TestClient

app = FastAPI()
ORDERS = {1: {"id": 1, "customer": "budi@mail.com", "total": 900_000},
          2: {"id": 2, "customer": "ani@mail.com", "total": 4_500_000,
              "address": "Jl. Melati 7, Bandung"}}
ADMINS = {"admin@toko.com"}


def current_user(x_user: str = Header()) -> str:
    return x_user                    # anggap: hasil login yang valid


def can_access(user: str, order: dict) -> bool:
    return order["customer"] == user or user in ADMINS


@app.get("/orders/{order_id}")
def get_order(order_id: int, user: str = Depends(current_user)):
    order = ORDERS.get(order_id)
    if order is None or not can_access(user, order):
        raise HTTPException(404, "order tidak ditemukan")
    return order


if __name__ == "__main__":
    client = TestClient(app)
    for user, order_id in [("budi@mail.com", 1), ("budi@mail.com", 2),
                           ("admin@toko.com", 2)]:
        response = client.get(f"/orders/{order_id}",
                              headers={"X-User": user})
        print(f"{user.split('@')[0]} GET /orders/{order_id} -> "
              f"{response.status_code} {response.json()}")
