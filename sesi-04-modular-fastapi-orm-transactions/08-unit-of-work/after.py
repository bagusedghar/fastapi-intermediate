"""Unit of Work - AFTER

Unit of Work (UoW) memegang session dan semua repository dalam satu transaksi.
- repository TIDAK commit sendiri
- service menentukan kapan selesai dengan uow.commit()
- keluar dari `with uow:` tanpa commit (misalnya karena error) = rollback
Service juga tidak perlu tahu soal SQLAlchemy Session, cukup tahu uow.
"""
from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


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


class ProductRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, product_id: int) -> ProductRecord:
        return self.session.get(ProductRecord, product_id)


class OrderRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, customer: str) -> None:
        self.session.add(OrderRecord(customer=customer))


class UnitOfWork:
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory

    def __enter__(self) -> "UnitOfWork":
        self.session = self.session_factory()
        self.products = ProductRepository(self.session)
        self.orders = OrderRepository(self.session)
        return self

    def __exit__(self, *exc) -> None:
        self.session.rollback()        # tidak berefek kalau sudah commit
        self.session.close()

    def commit(self) -> None:
        self.session.commit()


class OrderService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def place_order(self, customer: str, items: list[tuple[int, int]]) -> None:
        with self.uow:
            for product_id, qty in items:
                product = self.uow.products.get(product_id)
                if qty > product.stock:
                    raise ValueError(f"Stok {product.name} tidak cukup")
                product.stock -= qty
            self.uow.orders.add(customer)
            self.uow.commit()                      # satu commit untuk semua langkah


if __name__ == "__main__":
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(engine)
    with SessionLocal() as session:
        session.add_all([ProductRecord(name="Keyboard", stock=5), ProductRecord(name="Mouse", stock=1)])
        session.commit()

    service = OrderService(UnitOfWork(SessionLocal))
    try:
        service.place_order("budi@mail.com", [(1, 2), (2, 3)])
    except ValueError as e:
        print("Gagal:", e)

    with SessionLocal() as session:
        print("Stok Keyboard:", session.get(ProductRecord, 1).stock)   # 5, tidak berubah
