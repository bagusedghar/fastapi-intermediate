"""N+1 Query - BEFORE

Menampilkan 100 order terbaru beserta item-nya.
Relationship `lines` di-load secara lazy: item baru diambil saat order.lines diakses.
1 query untuk 100 order + 100 query untuk item masing-masing order = 101 query.
Kodenya terlihat wajar, masalahnya baru kelihatan kalau query-nya dihitung.

Butuh PostgreSQL + data demo: docker compose up -d, lalu python seed_demo.py (dari folder sesi-07)
Jalankan demo: python before.py
"""
import os
import time

from sqlalchemy import ForeignKey, create_engine, event, select, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

engine = create_engine(os.getenv("DEMO_DATABASE_URL", "postgresql+psycopg://app:app@localhost:5432/demo"))
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
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    price: Mapped[int]
    qty: Mapped[int]


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer: Mapped[str]
    lines: Mapped[list[OrderLine]] = relationship()      # default: lazy load


def latest_orders(session: Session) -> list[dict]:
    orders = session.scalars(select(Order).order_by(Order.id.desc()).limit(100))
    return [{"id": o.id, "total": sum(line.price * line.qty for line in o.lines)}   # query lagi di sini
            for o in orders]


if __name__ == "__main__":
    with engine.begin() as conn:      # index foreign key, supaya yang dibandingkan cuma jumlah query
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_order_lines_order_id ON order_lines (order_id)"))
    queries = 0

    with Session(engine) as session:
        start = time.perf_counter()
        result = latest_orders(session)
        print(f"{len(result)} order, {queries} query, {(time.perf_counter() - start) * 1000:.0f} ms")
