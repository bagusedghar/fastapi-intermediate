"""Transaction Boundary - AFTER

Semua langkah (kurangi stok semua item + simpan order) ada dalam SATU transaksi.
`with session.begin():` otomatis:
- commit kalau semua langkah berhasil
- rollback kalau ada error di tengah jalan
Hasilnya atomic: berhasil semua, atau tidak ada yang berubah sama sekali.
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
    with session.begin():  # transaction boundary
        for product_id, qty in items:
            product = session.get(ProductRecord, product_id)
            if qty > product.stock:
                raise ValueError(
                    f"Stok {product.name} tidak cukup"
                )
            product.stock -= qty

        session.add(OrderRecord(customer=customer))
    # sampai sini tanpa error = commit, ada error = rollback


if __name__ == "__main__":
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        with session.begin():
            session.add_all([
                ProductRecord(name="Keyboard", stock=5),
                ProductRecord(name="Mouse", stock=1),
            ])

        try:
            items = [(1, 2), (2, 3)]  # Mouse cuma 1, diminta 3
            place_order(session, "budi@mail.com", items)
        except ValueError as e:
            print("Gagal:", e)

        keyboard = session.get(ProductRecord, 1)
        print("Stok Keyboard:", keyboard.stock)  # tetap 5
        orders = session.scalars(select(OrderRecord)).all()
        print("Jumlah order:", len(orders))  # 0
