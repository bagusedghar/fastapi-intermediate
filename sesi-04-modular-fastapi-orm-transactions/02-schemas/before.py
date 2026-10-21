"""Schemas - BEFORE

Satu model Product dipakai untuk request dan response sekaligus.
- client bisa mengirim "id" sendiri
- response ikut membocorkan cost_price (harga modal) yang seharusnya internal

Jalankan: uvicorn before:app --reload
"""
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
PRODUCTS: dict[int, dict] = {}


class Product(BaseModel):
    id: int
    name: str
    price: int
    cost_price: int      # harga modal, hanya untuk internal
    stock: int


@app.post("/products", status_code=201)
def create_product(product: Product):
    PRODUCTS[product.id] = product.model_dump()
    return PRODUCTS[product.id]          # cost_price ikut terkirim ke client


@app.get("/products/{product_id}")
def get_product(product_id: int):
    return PRODUCTS[product_id]
