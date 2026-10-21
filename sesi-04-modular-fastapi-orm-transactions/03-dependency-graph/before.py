"""Dependency Graph - BEFORE

Setiap route membuat session, repository, dan service sendiri.
Kodenya berulang di semua route, dan kalau terjadi error sebelum close(),
session tidak pernah ditutup (koneksi bocor).

Jalankan: uvicorn before:app --reload
"""
from fastapi import FastAPI
from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
SessionLocal = sessionmaker(engine)


class Base(DeclarativeBase):
    pass


class ProductRecord(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[int]


Base.metadata.create_all(engine)


class ProductRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, name: str, price: int) -> ProductRecord:
        record = ProductRecord(name=name, price=price)
        self.session.add(record)
        self.session.commit()
        return record

    def list(self) -> list[ProductRecord]:
        return list(self.session.query(ProductRecord))


app = FastAPI()


@app.post("/products", status_code=201)
def create_product(name: str, price: int):
    session = SessionLocal()                 # dibuat manual...
    repo = ProductRepository(session)
    record = repo.add(name, price)
    result = {"id": record.id, "name": record.name, "price": record.price}
    session.close()                          # tidak jalan kalau ada error di atas
    return result


@app.get("/products")
def list_products():
    session = SessionLocal()                 # ...dan diulang di setiap route
    repo = ProductRepository(session)
    result = [{"id": r.id, "name": r.name, "price": r.price} for r in repo.list()]
    session.close()
    return result
