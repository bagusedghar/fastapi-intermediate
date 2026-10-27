"""Transaction Boundary - BEFORE

Order berisi 2 produk. Stok dikurangi per item, dan setiap item langsung di-commit.
Item kedua ternyata stoknya kurang, jadi order gagal dibuat...
tapi stok item pertama SUDAH terlanjur berkurang di database.
Data jadi tidak konsisten: stok hilang tanpa ada order-nya.
"""
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, Session, mapped_column,
)


class Base(DeclarativeBase):
    pass


class ProductRecord(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    stock: Mapped[int]


class OrderRecord(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer: Mapped[str] = mapped_column(String(100))


def place_order(
    session: Session, customer: str, items: list[tuple[int, int]]
) -> None:
    for product_id, qty in items:
        product = session.get(ProductRecord, product_id)
        if qty > product.stock:
            raise ValueError(
                f"Stok {product.name} tidak cukup"
            )
        product.stock -= qty
        session.commit()  # commit di tengah proses

    session.add(OrderRecord(customer=customer))
    session.commit()


if __name__ == "__main__":
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add_all([
            ProductRecord(name="Keyboard", stock=5),
            ProductRecord(name="Mouse", stock=1),
        ])
        session.commit()

        try:
            items = [(1, 2), (2, 3)]  # Mouse cuma 1, diminta 3
            place_order(session, "budi@mail.com", items)
        except ValueError as e:
            print("Gagal:", e)

        session.rollback()
        keyboard = session.get(ProductRecord, 1)
        print("Stok Keyboard:", keyboard.stock)  # 3, harusnya 5
        orders = session.scalars(select(OrderRecord)).all()
        print("Jumlah order:", len(orders))  # 0
