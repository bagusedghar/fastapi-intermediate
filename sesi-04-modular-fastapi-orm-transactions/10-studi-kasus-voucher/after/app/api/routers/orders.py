"""API: endpoint order.

Tidak ada try/except di sini. Error dari service naik ke exception handler global (api/errors.py).
"""
from fastapi import APIRouter, Depends

from app.api.dependencies import get_order_service
from app.api.schemas import ErrorOut, OrderIn, OrderOut
from app.application.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["orders"])

NOT_FOUND = {404: {"model": ErrorOut, "description": "Order, produk, atau voucher tidak ditemukan"}}
CONFLICT = {409: {"model": ErrorOut, "description": "Stok kurang, kuota voucher habis, atau status order tidak sesuai"}}


@router.post("", status_code=201, response_model=OrderOut, summary="Buat order",
             responses={400: {"model": ErrorOut, "description": "Tipe customer tidak dikenal"},
                        **NOT_FOUND, **CONFLICT})
def create_order(payload: OrderIn, service: OrderService = Depends(get_order_service)):
    items = [i.model_dump() for i in payload.items]
    order = service.place_order(payload.customer, payload.customer_type, items, payload.voucher_code)
    return OrderOut.from_domain(order)


@router.get("/{order_id}", response_model=OrderOut, summary="Detail order", responses=NOT_FOUND)
def get_order(order_id: int, service: OrderService = Depends(get_order_service)):
    return OrderOut.from_domain(service.get_order(order_id))


@router.post("/{order_id}/pay", response_model=OrderOut, summary="Bayar order",
             responses={**NOT_FOUND, **CONFLICT})
def pay_order(order_id: int, service: OrderService = Depends(get_order_service)):
    return OrderOut.from_domain(service.pay_order(order_id))


@router.post("/{order_id}/cancel", response_model=OrderOut, summary="Batalkan order (stok dan kuota voucher dikembalikan)",
             responses={**NOT_FOUND, **CONFLICT})
def cancel_order(order_id: int, service: OrderService = Depends(get_order_service)):
    return OrderOut.from_domain(service.cancel_order(order_id))
