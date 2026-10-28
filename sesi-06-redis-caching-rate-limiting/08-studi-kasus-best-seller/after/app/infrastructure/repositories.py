"""Infrastructure: adapter SQLAlchemy untuk port repository.

Repository menerjemahkan domain model <-> ORM model, dan TIDAK pernah commit.
Commit adalah keputusan Unit of Work.
Product repository mencatat id produk yang berubah, supaya Unit of Work bisa menghapus cache-nya.
Order repository mencatat apakah ada status order yang berubah (untuk cache produk terlaris).
"""
import time

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.money import Money
from app.domain.order import Order, OrderLine, OrderStatus
from app.domain.product import Product
from app.infrastructure.config import get_settings
from app.infrastructure.models import OrderLineRecord, OrderRecord, ProductRecord


class SqlAlchemyProductRepository:
    def __init__(self, session: Session):
        self.session = session
        self.changed_ids: set[int] = set()

    def add(self, product: Product) -> Product:
        record = ProductRecord(name=product.name, price=product.price.amount, stock=product.stock)
        self.session.add(record)
        self.session.flush()                  # minta id dari database, belum commit
        product.id = record.id
        self.changed_ids.add(product.id)
        return product

    def get(self, product_id: int) -> Product | None:
        time.sleep(get_settings().query_delay)     # simulasi query berat
        record = self.session.get(ProductRecord, product_id)
        return self._to_domain(record) if record else None

    def list(self) -> list[Product]:
        time.sleep(get_settings().query_delay)     # simulasi query berat
        records = self.session.scalars(select(ProductRecord).order_by(ProductRecord.id))
        return [self._to_domain(r) for r in records]

    def save(self, product: Product) -> None:
        self.session.get(ProductRecord, product.id).stock = product.stock
        self.changed_ids.add(product.id)

    @staticmethod
    def _to_domain(record: ProductRecord) -> Product:
        return Product(record.name, Money(record.price), record.stock, id=record.id)


class SqlAlchemyOrderRepository:
    def __init__(self, session: Session):
        self.session = session
        self.status_changed = False

    def add(self, order: Order) -> Order:
        record = OrderRecord(
            customer=order.customer, customer_type=order.customer_type,
            status=order.status.value, discount=order.discount.amount,
            lines=[OrderLineRecord(product_id=line.product_id, product=line.product,
                                   price=line.price.amount, qty=line.qty) for line in order.lines],
        )
        self.session.add(record)
        self.session.flush()
        order.id = record.id
        return order

    def get(self, order_id: int) -> Order | None:
        record = self.session.get(OrderRecord, order_id)
        return self._to_domain(record) if record else None

    def best_sellers(self, limit: int) -> list[dict]:
        time.sleep(get_settings().query_delay)     # simulasi query berat
        sold = func.sum(OrderLineRecord.qty).label("sold")
        rows = self.session.execute(
            select(OrderLineRecord.product_id, OrderLineRecord.product, sold)
            .join(OrderRecord, OrderRecord.id == OrderLineRecord.order_id)
            .where(OrderRecord.status == OrderStatus.PAID.value)
            .group_by(OrderLineRecord.product_id, OrderLineRecord.product)
            .order_by(sold.desc(), OrderLineRecord.product_id)
            .limit(limit)
        )
        return [{"product_id": r.product_id, "name": r.product, "sold": r.sold} for r in rows]

    def list(self) -> list[Order]:
        records = self.session.scalars(select(OrderRecord).order_by(OrderRecord.id))
        return [self._to_domain(r) for r in records]

    def save(self, order: Order) -> None:
        # setelah dibuat, yang bisa berubah dari order cuma status-nya
        self.session.get(OrderRecord, order.id).status = order.status.value
        self.status_changed = True

    @staticmethod
    def _to_domain(record: OrderRecord) -> Order:
        lines = [OrderLine(line.product_id, line.product, Money(line.price), line.qty) for line in record.lines]
        return Order(record.customer, record.customer_type, id=record.id, status=OrderStatus(record.status),
                     lines=lines, discount=Money(record.discount))
