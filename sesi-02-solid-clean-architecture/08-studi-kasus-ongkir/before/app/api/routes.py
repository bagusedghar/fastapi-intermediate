"""API: route hanya menghandle HTTP (request, response, status code)."""
from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.dependencies import get_order_service
from app.application.order_service import OrderNotFound, OrderService
from app.domain.discounts import UnknownCustomerType

router = APIRouter(prefix="/orders", tags=["orders"])


class Item(BaseModel):
    name: str
    price: int = Field(gt=0)
    qty: int = Field(gt=0)


class OrderIn(BaseModel):
    customer: str
    customer_type: str = "regular"
    items: list[Item]


@router.post("", status_code=201)
def create_order(payload: OrderIn, service: OrderService = Depends(get_order_service)):
    try:
        items = [i.model_dump() for i in payload.items]
        return asdict(service.place_order(payload.customer, payload.customer_type, items))
    except UnknownCustomerType as e:
        raise HTTPException(400, str(e))


@router.get("/{order_id}")
def get_order(order_id: int, service: OrderService = Depends(get_order_service)):
    try:
        return asdict(service.get_order(order_id))
    except OrderNotFound as e:
        raise HTTPException(404, str(e))
