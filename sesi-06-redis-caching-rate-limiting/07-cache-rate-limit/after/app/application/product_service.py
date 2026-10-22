"""Application: use case product.

Baca produk memakai cache-aside: cek cache dulu, kalau tidak ada baru ke database lalu simpan ke cache.
Cache dihapus (invalidation) oleh Unit of Work setiap ada produk yang berubah, setelah commit.
"""
from app.application.cache_keys import PRODUCT_LIST_KEY, product_key
from app.application.errors import ProductNotFound
from app.application.ports import Cache, UnitOfWork
from app.domain.money import Money
from app.domain.product import Product


class ProductService:
    def __init__(self, uow: UnitOfWork, cache: Cache):
        self.uow = uow
        self.cache = cache

    def create_product(self, name: str, price: int, stock: int) -> Product:
        with self.uow:
            product = self.uow.products.add(Product(name, Money(price), stock))
            self.uow.commit()
        return product

    def list_products(self) -> list[Product]:
        cached = self.cache.get(PRODUCT_LIST_KEY)
        if cached is not None:
            return [_from_dict(row) for row in cached]

        with self.uow:
            products = self.uow.products.list()
        self.cache.set(PRODUCT_LIST_KEY, [_to_dict(p) for p in products])
        return products

    def get_product(self, product_id: int) -> Product:
        cached = self.cache.get(product_key(product_id))
        if cached is not None:
            return _from_dict(cached)

        with self.uow:
            product = self.uow.products.get(product_id)
        if product is None:
            raise ProductNotFound(f"Product #{product_id} tidak ditemukan")
        self.cache.set(product_key(product_id), _to_dict(product))
        return product


def _to_dict(product: Product) -> dict:
    return {"id": product.id, "name": product.name, "price": product.price.amount, "stock": product.stock}


def _from_dict(row: dict) -> Product:
    return Product(row["name"], Money(row["price"]), row["stock"], id=row["id"])
