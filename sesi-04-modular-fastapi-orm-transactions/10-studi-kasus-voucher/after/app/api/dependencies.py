"""API: dependency graph.

get_session_factory -> get_uow -> get_order_service / get_product_service / get_voucher_service -> route
Di test, cukup override get_session_factory (database di memory) dan get_notifier.
"""
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.orm import sessionmaker

from app.application.order_service import OrderService
from app.application.ports import Notifier, UnitOfWork
from app.application.product_service import ProductService
from app.application.voucher_service import VoucherService
from app.infrastructure.config import get_settings
from app.infrastructure.database import create_session_factory
from app.infrastructure.notifiers import create_notifier
from app.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


@lru_cache
def get_session_factory() -> sessionmaker:
    return create_session_factory(get_settings().database_url)


def get_uow(session_factory: sessionmaker = Depends(get_session_factory)) -> UnitOfWork:
    return SqlAlchemyUnitOfWork(session_factory)


def get_notifier() -> Notifier:
    return create_notifier(get_settings().notification_channel)


def get_order_service(uow: UnitOfWork = Depends(get_uow),
                      notifier: Notifier = Depends(get_notifier)) -> OrderService:
    return OrderService(uow, notifier)


def get_product_service(uow: UnitOfWork = Depends(get_uow)) -> ProductService:
    return ProductService(uow)


def get_voucher_service(uow: UnitOfWork = Depends(get_uow)) -> VoucherService:
    return VoucherService(uow)
