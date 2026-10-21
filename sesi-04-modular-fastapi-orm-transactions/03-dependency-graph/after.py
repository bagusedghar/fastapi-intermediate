"""Dependency Graph - AFTER

Dependency disusun berantai: get_session -> get_repository -> route.
- get_session memakai yield: kode setelah yield SELALU jalan setelah response,
  walaupun terjadi error. Jadi session pasti ditutup.
- FastAPI membuat satu session per request dan memakainya untuk semua dependency di request itu.
- route cukup minta repository, tidak perlu tahu cara membuatnya.

Jalankan: uvicorn after:app --reload
"""
from collections.abc import Iterator

from fastapi import Depends, FastAPI
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


# ---------- dependencies ----------
def get_session() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()                      # selalu jalan, error atau tidak


def get_repository(session: Session = Depends(get_session)) -> ProductRepository:
    return ProductRepository(session)


# ---------- routes ----------
app = FastAPI()


@app.post("/products", status_code=201)
def create_product(name: str, price: int, repo: ProductRepository = Depends(get_repository)):
    record = repo.add(name, price)
    return {"id": record.id, "name": record.name, "price": record.price}


@app.get("/products")
def list_products(repo: ProductRepository = Depends(get_repository)):
    return [{"id": r.id, "name": r.name, "price": r.price} for r in repo.list()]
