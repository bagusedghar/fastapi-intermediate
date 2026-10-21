"""Schemas - AFTER

Schema request dan response dipisah:
- ProductIn  : yang boleh dikirim client (tanpa id)
- ProductOut : yang boleh dilihat client (tanpa cost_price)
response_model memastikan field di luar ProductOut tidak ikut terkirim,
dan validasi (price > 0, stock >= 0) langsung tercatat di dokumentasi OpenAPI.

Jalankan: uvicorn after:app --reload
"""
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()
PRODUCTS: dict[int, dict] = {}


class ProductIn(BaseModel):
    name: str = Field(min_length=1)
    price: int = Field(gt=0)
    cost_price: int = Field(gt=0)
    stock: int = Field(ge=0)


class ProductOut(BaseModel):
    id: int
    name: str
    price: int
    stock: int


@app.post("/products", status_code=201, response_model=ProductOut)
def create_product(payload: ProductIn):
    product = {"id": len(PRODUCTS) + 1, **payload.model_dump()}
    PRODUCTS[product["id"]] = product
    return product                       # cost_price disaring oleh response_model


@app.get("/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int):
    return PRODUCTS[product_id]
