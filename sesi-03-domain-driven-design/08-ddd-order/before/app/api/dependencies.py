"""API: tempat menyiapkan dependency. Di test, function di sini bisa di-override."""
from functools import lru_cache

from fastapi import Depends

from app.application.order_service import OrderService
from app.application.ports import Notifier, OrderRepository
from app.infrastructure.config import get_settings
from app.infrastructure.notifiers import create_notifier
from app.infrastructure.sqlite_repository import SqliteOrderRepository


@lru_cache
def get_repository() -> OrderRepository:
    return SqliteOrderRepository(get_settings().database_path)


def get_notifier() -> Notifier:
    return create_notifier(get_settings().notification_channel)


def get_order_service(
    repo: OrderRepository = Depends(get_repository),
    notifier: Notifier = Depends(get_notifier),
) -> OrderService:
    return OrderService(repo, notifier)
