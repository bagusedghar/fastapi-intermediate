"""N+1 Query - AFTER

selectinload(Order.lines) mengambil item SEMUA order sekaligus dalam satu query tambahan:
    SELECT ... FROM order_lines WHERE order_id IN (1, 2, 3, ...)
Jumlah query tetap 2, berapa pun banyaknya order.

Pilihan lain: joinedload (satu query dengan JOIN), cocok untuk relasi many-to-one.
Untuk relasi one-to-many seperti order -> lines, selectinload biasanya lebih efisien.

Index di order_lines.order_id juga penting. PostgreSQL TIDAK otomatis membuat index untuk foreign key,
jadi tanpa index, query "WHERE order_id IN (...)" tetap membaca seluruh tabel order_lines.

Butuh PostgreSQL + data dummy: docker compose up -d, lalu python seed_demo.py (dari folder sesi-07)
Jalankan demo: python after.py
"""
import os
import time

from sqlalchemy import ForeignKey, create_engine, event, select, text
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, Session, mapped_column, relationship,
    selectinload,
)

DB_URL = os.getenv("DEMO_DATABASE_URL",
                   "postgresql+psycopg://app:app@localhost:5432/demo")
engine = create_engine(DB_URL)
queries = 0


@event.listens_for(engine, "before_cursor_execute")
def count_query(*args):
    global queries
    queries += 1


class Base(DeclarativeBase):
    pass


class OrderLine(Base):
    __tablename__ = "order_lines"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"),
                                          index=True)
    price: Mapped[int]
    qty: Mapped[int]


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer: Mapped[str]
    lines: Mapped[list[OrderLine]] = relationship()


def latest_orders(session: Session) -> list[dict]:
    query = (select(Order).options(selectinload(Order.lines))
             .order_by(Order.id.desc()).limit(100))
    orders = session.scalars(query)
    return [{"id": o.id,
             "total": sum(line.price * line.qty
                          for line in o.lines)}
            for o in orders]


if __name__ == "__main__":
    with engine.begin() as conn:  # index FK, lihat catatan di atas
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_order_lines_order_id"
            " ON order_lines (order_id)"))
    queries = 0

    with Session(engine) as session:
        start = time.perf_counter()
        result = latest_orders(session)
        ms = (time.perf_counter() - start) * 1000
        print(f"{len(result)} order, {queries} query, {ms:.0f} ms")
