"""Fake adapter untuk unit test use case. Bentuknya sama dengan port, isinya cuma dict."""
from app.domain.order import Order
from app.domain.product import Product
from app.domain.voucher import Voucher


class FakeProductRepository:
    def __init__(self, products: list[Product] = ()):
        self.rows: dict[int, Product] = {}
        for product in products:
            self.add(product)

    def add(self, product: Product) -> Product:
        product.id = len(self.rows) + 1
        self.rows[product.id] = product
        return product

    def get(self, product_id: int) -> Product | None:
        return self.rows.get(product_id)

    def list(self) -> list[Product]:
        return list(self.rows.values())

    def save(self, product: Product) -> None:
        self.rows[product.id] = product


class FakeOrderRepository:
    def __init__(self):
        self.rows: dict[int, Order] = {}

    def add(self, order: Order) -> Order:
        order.id = len(self.rows) + 1
        self.rows[order.id] = order
        return order

    def get(self, order_id: int) -> Order | None:
        return self.rows.get(order_id)

    def save(self, order: Order) -> None:
        self.rows[order.id] = order


class FakeVoucherRepository:
    def __init__(self, vouchers: list[Voucher] = ()):
        self.rows: dict[str, Voucher] = {v.code: v for v in vouchers}

    def add(self, voucher: Voucher) -> Voucher:
        self.rows[voucher.code] = voucher
        return voucher

    def get(self, code: str) -> Voucher | None:
        return self.rows.get(code)

    def save(self, voucher: Voucher) -> None:
        self.rows[voucher.code] = voucher


class FakeUnitOfWork:
    def __init__(self, products: list[Product] = (), vouchers: list[Voucher] = ()):
        self.products = FakeProductRepository(products)
        self.orders = FakeOrderRepository()
        self.vouchers = FakeVoucherRepository(vouchers)
        self.committed = False

    def __enter__(self) -> "FakeUnitOfWork":
        return self

    def __exit__(self, *exc) -> None:
        pass

    def commit(self) -> None:
        self.committed = True


class FakeNotifier:
    def __init__(self):
        self.sent: list[tuple[str, str]] = []

    def send(self, to: str, message: str) -> None:
        self.sent.append((to, message))
