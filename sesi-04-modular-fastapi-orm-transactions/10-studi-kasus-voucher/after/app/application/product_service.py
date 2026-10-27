"""Application: use case product."""
from app.application.errors import ProductNotFound
from app.application.ports import UnitOfWork
from app.domain.money import Money
from app.domain.product import Product


class ProductService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    def create_product(self, name: str, price: int, stock: int) -> Product:
        with self.uow:
            product = self.uow.products.add(Product(name, Money(price), stock))
            self.uow.commit()
        return product

    def list_products(self) -> list[Product]:
        with self.uow:
            return self.uow.products.list()

    def get_product(self, product_id: int) -> Product:
        with self.uow:
            product = self.uow.products.get(product_id)
        if product is None:
            raise ProductNotFound(f"Product #{product_id} tidak ditemukan")
        return product
