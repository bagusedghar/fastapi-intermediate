"""Input Validation - AFTER (schema Pydantic yang ketat)

Body divalidasi oleh schema sebelum masuk ke kode endpoint:
- Field(gt=0, le=100)     : qty harus 1 sampai 100
- Literal[...]            : customer_type hanya nilai yang dikenal
- extra="forbid"          : field yang tidak ada di schema (misalnya price) ditolak, bukan diabaikan
Harga selalu diambil dari database, tidak pernah dari body request.
Data yang tidak valid dijawab 422 sebelum kode endpoint berjalan.

Jalankan: python after.py
"""
from typing import Literal

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict, Field

PRODUCTS = {1: {"name": "Keyboard", "price": 500_000}}
app = FastAPI()


class OrderIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product_id: int = Field(gt=0)
    qty: int = Field(gt=0, le=100)
    customer_type: Literal["regular", "member", "vip"]


@app.post("/orders", status_code=201)
def create_order(body: OrderIn):
    price = PRODUCTS[body.product_id]["price"]       # dari database
    return {"customer_type": body.customer_type,
            "total": price * body.qty}


if __name__ == "__main__":
    client = TestClient(app)
    for body in [{"product_id": 1, "qty": -5, "customer_type": "vip"},
                 {"product_id": 1, "qty": 2, "price": 1,
                  "customer_type": "reseller"},
                 {"product_id": 1, "qty": 2, "customer_type": "vip"}]:
        response = client.post("/orders", json=body)
        result = response.json()
        if response.status_code == 422:
            result = [f"{e['loc'][-1]}: {e['msg']}"
                      for e in result["detail"]]
        print(f"{body}\n  -> {response.status_code} {result}")
