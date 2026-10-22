"""API: endpoint product."""
from fastapi import APIRouter, Depends

from app.api.dependencies import get_product_service
from app.api.schemas import ErrorOut, ProductIn, ProductOut
from app.application.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", status_code=201, response_model=ProductOut, summary="Tambah produk")
def create_product(payload: ProductIn, service: ProductService = Depends(get_product_service)):
    return ProductOut.from_domain(service.create_product(payload.name, payload.price, payload.stock))


@router.get("", response_model=list[ProductOut], summary="Daftar produk")
def list_products(service: ProductService = Depends(get_product_service)):
    return [ProductOut.from_domain(p) for p in service.list_products()]


@router.get("/{product_id}", response_model=ProductOut, summary="Detail produk",
            responses={404: {"model": ErrorOut, "description": "Produk tidak ditemukan"}})
def get_product(product_id: int, service: ProductService = Depends(get_product_service)):
    return ProductOut.from_domain(service.get_product(product_id))
