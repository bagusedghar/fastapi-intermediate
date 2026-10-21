"""API: route hanya menghandle HTTP (request, response, status code).
Error dari domain diterjemahkan ke status code yang sesuai.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.dependencies import get_order_service
from app.application.order_service import OrderNotFound, OrderService
from app.domain.discount_policy import UnknownCustomerType
from app.domain.order import Order, OrderCannotBeChanged

router = APIRouter(prefix="/orders", tags=["orders"])


class Item(BaseModel):
    name: str
    price: int = Field(gt=0)
    qty: int = Field(gt=0)


class OrderIn(BaseModel):
    customer: str
    customer_type: str = "regular"
    items: list[Item] = Field(min_length=1)


def to_response(order: Order) -> dict:
    return {
        "id": order.id,
        "customer": order.customer,
        "customer_type": order.customer_type,
        "status": order.status.value,
        "items": [{"name": line.product, "price": line.price.amount, "qty": line.qty}
                  for line in order.lines],
        "subtotal": order.subtotal.amount,
        "discount": order.discount.amount,
        "total": order.total.amount,
    }


@router.post("", status_code=201)
def create_order(payload: OrderIn, service: OrderService = Depends(get_order_service)):
    try:
        items = [i.model_dump() for i in payload.items]
        return to_response(service.place_order(payload.customer, payload.customer_type, items))
    except UnknownCustomerType as e:
        raise HTTPException(400, str(e))


@router.get("/{order_id}")
def get_order(order_id: int, service: OrderService = Depends(get_order_service)):
    try:
        return to_response(service.get_order(order_id))
    except OrderNotFound as e:
        raise HTTPException(404, str(e))


@router.post("/{order_id}/pay")
def pay_order(order_id: int, service: OrderService = Depends(get_order_service)):
    try:
        return to_response(service.pay_order(order_id))
    except OrderNotFound as e:
        raise HTTPException(404, str(e))
    except OrderCannotBeChanged as e:
        raise HTTPException(409, str(e))


@router.post("/{order_id}/cancel")
def cancel_order(order_id: int, service: OrderService = Depends(get_order_service)):
    try:
        return to_response(service.cancel_order(order_id))
    except OrderNotFound as e:
        raise HTTPException(404, str(e))
    except OrderCannotBeChanged as e:
        raise HTTPException(409, str(e))
