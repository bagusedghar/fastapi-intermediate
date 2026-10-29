"""API: endpoint product. Melihat produk terbuka untuk umum, menambah produk butuh scope products:write."""
from fastapi import APIRouter, Depends, Security

from app.api.dependencies import get_product_service
from app.api.schemas import ErrorOut, ProductIn, ProductOut
from app.api.security import get_current_user
from app.application.product_service import ProductService

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", status_code=201, response_model=ProductOut, summary="Tambah produk (admin)",
             dependencies=[Security(get_current_user, scopes=["products:write"])],
             responses={401: {"model": ErrorOut, "description": "Belum login"},
                        403: {"model": ErrorOut, "description": "Butuh scope products:write"}})
def create_product(payload: ProductIn, service: ProductService = Depends(get_product_service)):
    return ProductOut.from_domain(service.create_product(payload.name, payload.price, payload.stock))


@router.get("", response_model=list[ProductOut], summary="Daftar produk")
def list_products(service: ProductService = Depends(get_product_service)):
    return [ProductOut.from_domain(p) for p in service.list_products()]


@router.get("/{product_id}", response_model=ProductOut, summary="Detail produk",
            responses={404: {"model": ErrorOut, "description": "Produk tidak ditemukan"}})
def get_product(product_id: int, service: ProductService = Depends(get_product_service)):
    return ProductOut.from_domain(service.get_product(product_id))
