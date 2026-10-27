"""Infrastructure: adapter SQLAlchemy untuk port repository.

Repository menerjemahkan domain model <-> ORM model, dan TIDAK pernah commit.
Commit adalah keputusan Unit of Work.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.money import Money
from app.domain.order import Order, OrderLine, OrderStatus
from app.domain.product import Product
from app.domain.voucher import Voucher
from app.infrastructure.models import OrderLineRecord, OrderRecord, ProductRecord, VoucherRecord


class SqlAlchemyProductRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, product: Product) -> Product:
        record = ProductRecord(name=product.name, price=product.price.amount, stock=product.stock)
        self.session.add(record)
        self.session.flush()                  # minta id dari database, belum commit
        product.id = record.id
        return product

    def get(self, product_id: int) -> Product | None:
        record = self.session.get(ProductRecord, product_id)
        return self._to_domain(record) if record else None

    def list(self) -> list[Product]:
        records = self.session.scalars(select(ProductRecord).order_by(ProductRecord.id))
        return [self._to_domain(r) for r in records]

    def save(self, product: Product) -> None:
        self.session.get(ProductRecord, product.id).stock = product.stock

    @staticmethod
    def _to_domain(record: ProductRecord) -> Product:
        return Product(record.name, Money(record.price), record.stock, id=record.id)


class SqlAlchemyOrderRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, order: Order) -> Order:
        record = OrderRecord(
            customer=order.customer, customer_type=order.customer_type,
            status=order.status.value, discount=order.discount.amount, voucher_code=order.voucher_code,
            lines=[OrderLineRecord(product_id=line.product_id, product=line.product,
                                   price=line.price.amount, qty=line.qty) for line in order.lines],
        )
        self.session.add(record)
        self.session.flush()
        order.id = record.id
        return order

    def get(self, order_id: int) -> Order | None:
        record = self.session.get(OrderRecord, order_id)
        if record is None:
            return None
        lines = [OrderLine(line.product_id, line.product, Money(line.price), line.qty) for line in record.lines]
        return Order(record.customer, record.customer_type, id=record.id, status=OrderStatus(record.status),
                     lines=lines, discount=Money(record.discount), voucher_code=record.voucher_code)

    def save(self, order: Order) -> None:
        # setelah dibuat, yang bisa berubah dari order cuma status-nya
        self.session.get(OrderRecord, order.id).status = order.status.value


class SqlAlchemyVoucherRepository:
    def __init__(self, session: Session):
        self.session = session

    def add(self, voucher: Voucher) -> Voucher:
        self.session.add(VoucherRecord(code=voucher.code, amount=voucher.amount.amount, quota=voucher.quota))
        self.session.flush()
        return voucher

    def get(self, code: str) -> Voucher | None:
        record = self.session.get(VoucherRecord, code)
        return Voucher(record.code, Money(record.amount), record.quota) if record else None

    def save(self, voucher: Voucher) -> None:
        self.session.get(VoucherRecord, voucher.code).quota = voucher.quota
