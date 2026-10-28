"""API: dependency graph.

get_session_factory -> get_uow -> get_order_service / get_product_service -> route
get_session_factory ada di infrastructure, karena dipakai juga oleh worker Celery.
Notifier sekarang QueuedNotifier: notifikasi dikirim lewat queue, bukan di dalam request.
"""
from fastapi import Depends
from sqlalchemy.orm import sessionmaker

from app.application.order_service import OrderService
from app.application.ports import Notifier, UnitOfWork
from app.application.product_service import ProductService
from app.infrastructure.database import get_session_factory
from app.infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from app.worker.notifier import QueuedNotifier


def get_uow(session_factory: sessionmaker = Depends(get_session_factory)) -> UnitOfWork:
    return SqlAlchemyUnitOfWork(session_factory)


def get_notifier() -> Notifier:
    return QueuedNotifier()


def get_order_service(uow: UnitOfWork = Depends(get_uow),
                      notifier: Notifier = Depends(get_notifier)) -> OrderService:
    return OrderService(uow, notifier)


def get_product_service(uow: UnitOfWork = Depends(get_uow)) -> ProductService:
    return ProductService(uow)
