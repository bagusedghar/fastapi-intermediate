"""Domain Model vs ORM Model - AFTER

Dua class, dua tugas:
- Order       : domain model, berisi business logic, Python biasa tanpa SQLAlchemy
- OrderRecord : ORM model, cuma mewakili tabel orders
Repository yang menerjemahkan bolak-balik antara keduanya.
Struktur tabel bisa berubah tanpa menyentuh Order, dan Order bisa dites tanpa database.
"""
from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


# ---------- domain: tidak import SQLAlchemy ----------
class Order:
    def __init__(self, customer: str, total: int, status: str = "pending", id: int | None = None):
        self.id = id
        self.customer = customer
        self.total = total
        self.status = status

    def pay(self) -> None:
        if self.status != "pending":
            raise ValueError("Hanya order pending yang bisa dibayar")
        self.status = "paid"


# ---------- infrastructure: ORM model + repository ----------
class Base(DeclarativeBase):
    pass


class OrderRecord(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer: Mapped[str] = mapped_column(String(100))
    total: Mapped[int]
    status: Mapped[str] = mapped_column(String(20))


class SqlAlchemyOrderRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, order: Order) -> Order:
        record = OrderRecord(customer=order.customer, total=order.total, status=order.status)
        self.session.add(record)
        self.session.commit()
        order.id = record.id
        return order

    def get(self, order_id: int) -> Order | None:
        record = self.session.get(OrderRecord, order_id)
        return self._to_domain(record) if record else None

    def save(self, order: Order) -> None:
        record = self.session.get(OrderRecord, order.id)
        record.status = order.status
        self.session.commit()

    @staticmethod
    def _to_domain(record: OrderRecord) -> Order:
        return Order(record.customer, record.total, record.status, record.id)


if __name__ == "__main__":
    engine = create_engine("sqlite://")      # database di memory
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        repo = SqlAlchemyOrderRepository(session)
        order_id = repo.add(Order("budi@mail.com", 200_000)).id

        order = repo.get(order_id)    # dapat domain Order, bukan OrderRecord
        order.pay()                   # business logic tanpa tahu database
        repo.save(order)
        print(repo.get(order_id).status)
