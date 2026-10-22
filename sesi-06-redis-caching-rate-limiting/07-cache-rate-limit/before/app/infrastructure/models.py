"""Infrastructure: ORM model (bentuk tabel). Tidak berisi business logic."""
from datetime import datetime

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base


class ProductRecord(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[int]
    stock: Mapped[int]


class OrderRecord(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer: Mapped[str] = mapped_column(String(100))
    customer_type: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20))
    discount: Mapped[int]
    lines: Mapped[list["OrderLineRecord"]] = relationship(cascade="all, delete-orphan")


class OrderLineRecord(Base):
    __tablename__ = "order_lines"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    product: Mapped[str] = mapped_column(String(100))
    price: Mapped[int]
    qty: Mapped[int]


class SentNotificationRecord(Base):
    """Notifikasi yang sudah terkirim. key = idempotency key, unique karena primary key."""
    __tablename__ = "sent_notifications"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    sent_at: Mapped[datetime] = mapped_column(server_default=func.now())
