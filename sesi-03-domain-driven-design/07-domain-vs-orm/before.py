"""Domain Model vs ORM Model - BEFORE

OrderModel dipakai untuk dua urusan sekaligus:
tabel database (SQLAlchemy) dan tempat business logic (pay()).
- business logic ikut bergantung ke SQLAlchemy
- test pay() pun terasa harus lewat database
- nama kolom berubah, class business logic ikut diedit
"""
from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer: Mapped[str] = mapped_column(String(100))
    total: Mapped[int]
    status: Mapped[str] = mapped_column(String(20), default="pending")

    def pay(self) -> None:                  # business logic menempel di tabel
        if self.status != "pending":
            raise ValueError("Hanya order pending yang bisa dibayar")
        self.status = "paid"


if __name__ == "__main__":
    engine = create_engine("sqlite://")      # database di memory
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        order = OrderModel(customer="budi@mail.com", total=200_000, status="pending")
        session.add(order)
        session.commit()

        order.pay()
        session.commit()
        print(order.id, order.status)
