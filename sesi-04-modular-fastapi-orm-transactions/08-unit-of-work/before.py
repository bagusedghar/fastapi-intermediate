"""Unit of Work - BEFORE

Setiap repository commit sendiri di dalam save()/add().
Service tidak bisa menggabungkan beberapa langkah jadi satu transaksi:
begitu products.save() dipanggil, perubahan stok langsung permanen,
walaupun langkah berikutnya gagal.
"""
from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


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

    def save(self, product: ProductRecord) -> None:
        self.session.commit()                      # repository commit sendiri


class OrderRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, customer: str) -> None:
        self.session.add(OrderRecord(customer=customer))
        self.session.commit()                      # commit lagi


class OrderService:
    def __init__(self, products: ProductRepository, orders: OrderRepository):
        self.products = products
        self.orders = orders

    def place_order(self, customer: str, items: list[tuple[int, int]]) -> None:
        for product_id, qty in items:
            product = self.products.get(product_id)
            if qty > product.stock:
                raise ValueError(f"Stok {product.name} tidak cukup")
            product.stock -= qty
            self.products.save(product)           # langsung permanen
        self.orders.add(customer)


if __name__ == "__main__":
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    session = Session(engine)
    session.add_all([ProductRecord(name="Keyboard", stock=5), ProductRecord(name="Mouse", stock=1)])
    session.commit()

    service = OrderService(ProductRepository(session), OrderRepository(session))
    try:
        service.place_order("budi@mail.com", [(1, 2), (2, 3)])
    except ValueError as e:
        print("Gagal:", e)

    session.rollback()
    print("Stok Keyboard:", session.get(ProductRecord, 1).stock)   # 3, harusnya 5
