"""Broken Access Control - BEFORE (OWASP API #1: siapa pun bisa membaca order siapa pun)

User sudah login (di contoh ini disederhanakan lewat header X-User), tetapi endpoint
GET /orders/{order_id} hanya mencari order berdasarkan id, tanpa mengecek pemiliknya.
Budi cukup mengganti angka di URL untuk membaca order milik customer lain.
Celah ini disebut IDOR (Insecure Direct Object Reference).

Jalankan: python before.py
"""
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.testclient import TestClient

app = FastAPI()
ORDERS = {1: {"id": 1, "customer": "budi@mail.com", "total": 900_000},
          2: {"id": 2, "customer": "ani@mail.com", "total": 4_500_000,
              "address": "Jl. Melati 7, Bandung"}}


def current_user(x_user: str = Header()) -> str:
    return x_user                    # anggap: hasil login yang valid


@app.get("/orders/{order_id}")
def get_order(order_id: int, user: str = Depends(current_user)):
    order = ORDERS.get(order_id)
    if order is None:
        raise HTTPException(404, "order tidak ditemukan")
    return order


if __name__ == "__main__":
    client = TestClient(app)
    for order_id in (1, 2):
        response = client.get(f"/orders/{order_id}",
                              headers={"X-User": "budi@mail.com"})
        print(f"budi GET /orders/{order_id} -> {response.status_code} "
              f"{response.json()}")
