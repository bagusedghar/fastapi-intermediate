"""API: schema request & response (Pydantic). Ini juga yang tampil di /docs."""
from pydantic import BaseModel, Field

from app.domain.order import Order
from app.domain.product import Product
from app.domain.voucher import Voucher


# ---------- product ----------
class ProductIn(BaseModel):
    name: str = Field(min_length=1, examples=["Keyboard"])
    price: int = Field(gt=0, examples=[500_000])
    stock: int = Field(ge=0, examples=[10])


class ProductOut(BaseModel):
    id: int
    name: str
    price: int
    stock: int

    @classmethod
    def from_domain(cls, product: Product) -> "ProductOut":
        return cls(id=product.id, name=product.name, price=product.price.amount, stock=product.stock)


# ---------- order ----------
class OrderItemIn(BaseModel):
    product_id: int = Field(gt=0, examples=[1])
    qty: int = Field(gt=0, examples=[2])


class OrderIn(BaseModel):
    customer: str = Field(min_length=1, examples=["budi@mail.com"])
    customer_type: str = Field("regular", examples=["vip"])
    items: list[OrderItemIn] = Field(min_length=1)
    voucher_code: str | None = Field(None, examples=["HEMAT50"])


class OrderLineOut(BaseModel):
    product_id: int
    name: str
    price: int
    qty: int


class OrderOut(BaseModel):
    id: int
    customer: str
    customer_type: str
    status: str
    items: list[OrderLineOut]
    subtotal: int
    discount: int
    total: int
    voucher_code: str | None

    @classmethod
    def from_domain(cls, order: Order) -> "OrderOut":
        return cls(
            id=order.id, customer=order.customer, customer_type=order.customer_type,
            status=order.status.value,
            items=[OrderLineOut(product_id=line.product_id, name=line.product,
                                price=line.price.amount, qty=line.qty) for line in order.lines],
            subtotal=order.subtotal.amount, discount=order.discount.amount, total=order.total.amount,
            voucher_code=order.voucher_code,
        )


# ---------- voucher ----------
class VoucherIn(BaseModel):
    code: str = Field(min_length=3, max_length=30, examples=["HEMAT50"])
    amount: int = Field(gt=0, examples=[50_000])
    quota: int = Field(ge=0, examples=[2])


class VoucherOut(BaseModel):
    code: str
    amount: int
    quota: int

    @classmethod
    def from_domain(cls, voucher: Voucher) -> "VoucherOut":
        return cls(code=voucher.code, amount=voucher.amount.amount, quota=voucher.quota)


# ---------- error ----------
class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[dict] | None = None


class ErrorOut(BaseModel):
    error: ErrorBody
