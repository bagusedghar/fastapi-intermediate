"""Infrastructure: Unit of Work berbasis SQLAlchemy Session.

Satu `with uow:` = satu session = satu transaksi.
Semua repository di dalamnya memakai session yang sama.
"""
from sqlalchemy.orm import sessionmaker

from app.infrastructure.repositories import SqlAlchemyOrderRepository, SqlAlchemyProductRepository


class SqlAlchemyUnitOfWork:
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self.session = self.session_factory()
        self.orders = SqlAlchemyOrderRepository(self.session)
        self.products = SqlAlchemyProductRepository(self.session)
        return self

    def __exit__(self, *exc) -> None:
        self.session.rollback()      # sudah commit = tidak berefek, belum commit / error = dibatalkan
        self.session.close()

    def commit(self) -> None:
        self.session.commit()
