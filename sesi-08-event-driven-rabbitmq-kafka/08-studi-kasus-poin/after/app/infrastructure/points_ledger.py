"""Infrastructure: buku poin customer di database, adapter untuk port PointsLedger.

add() mencatat event_id dan menambah poin dalam SATU transaksi.
event_id adalah primary key di tabel point_events, jadi event yang sama tidak bisa tercatat dua kali:
INSERT kedua gagal (IntegrityError), seluruh transaksi di-rollback, dan poin tidak bertambah.
"""
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.infrastructure.models import CustomerPointsRecord, PointEventRecord


class SqlAlchemyPointsLedger:
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory

    def add(self, event_id: str, customer: str, points: int) -> bool:
        try:
            with self.session_factory.begin() as session:
                session.add(PointEventRecord(event_id=event_id, customer=customer, points=points))
                session.flush()                       # INSERT event dulu, gagal di sini jika sudah ada
                record = session.get(CustomerPointsRecord, customer)
                if record is None:
                    session.add(CustomerPointsRecord(customer=customer, points=points))
                else:
                    record.points += points
            return True
        except IntegrityError:
            return False                              # event sudah pernah diproses

    def balance(self, customer: str) -> int:
        with self.session_factory() as session:
            record = session.get(CustomerPointsRecord, customer)
            return record.points if record else 0
