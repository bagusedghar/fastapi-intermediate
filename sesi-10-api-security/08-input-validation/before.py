"""Input Validation - BEFORE (body diterima apa adanya)

Endpoint menerima body sebagai dict biasa, lalu memakainya langsung:
- qty negatif diterima, total order jadi minus
- client mengirim field "price" sendiri dan harga produk tertimpa (mass assignment)
- customer_type bebas diisi, termasuk tipe yang tidak ada

Jalankan: python before.py
"""
from fastapi import Body, FastAPI
from fastapi.testclient import TestClient

PRODUCTS = {1: {"name": "Keyboard", "price": 500_000}}
app = FastAPI()


@app.post("/orders", status_code=201)
def create_order(body: dict = Body()):
    item = {**PRODUCTS[body["product_id"]], **body}  # body menimpa data
    return {"customer_type": body["customer_type"],
            "total": item["price"] * item["qty"]}


if __name__ == "__main__":
    client = TestClient(app)
    for body in [{"product_id": 1, "qty": -5, "customer_type": "vip"},
                 {"product_id": 1, "qty": 2, "price": 1,
                  "customer_type": "reseller"}]:
        response = client.post("/orders", json=body)
        print(f"{body}\n  -> {response.status_code} {response.json()}")
