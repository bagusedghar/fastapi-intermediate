"""API: dependency graph.

get_session_factory -> get_uow -> get_order_service / get_product_service -> route
get_session_factory ada di infrastructure, karena dipakai juga oleh worker Celery.
Cache dan rate limiter memakai Redis yang sama (get_redis).
OrderService mengumumkan event lewat RabbitMQPublisher. Notifikasi dikirim oleh consumer, bukan oleh API.
get_health_checks berisi daftar dependency yang dicek readiness check. Di test, diganti dengan check palsu.
"""
from collections.abc import Callable

from fastapi import Depends
from sqlalchemy.orm import sessionmaker

from app.application.order_service import OrderService
from app.application.ports import Cache, EventPublisher, UnitOfWork
from app.application.product_service import ProductService
from app.infrastructure.cache import RedisCache
from app.infrastructure.config import get_settings
from app.infrastructure.database import get_session_factory
from app.infrastructure.health import check_database, check_rabbitmq, check_redis
from app.infrastructure.rabbitmq import RabbitMQPublisher
from app.infrastructure.rate_limiter import SlidingWindowRateLimiter
from app.infrastructure.redis_client import get_redis
from app.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


def get_cache() -> Cache:
    return RedisCache(get_redis(), get_settings().cache_ttl)


def get_uow(session_factory: sessionmaker = Depends(get_session_factory),
            cache: Cache = Depends(get_cache)) -> UnitOfWork:
    return SqlAlchemyUnitOfWork(session_factory, cache)


def get_event_publisher() -> EventPublisher:
    return RabbitMQPublisher(get_settings().rabbitmq_url)


def get_order_service(uow: UnitOfWork = Depends(get_uow),
                      events: EventPublisher = Depends(get_event_publisher)) -> OrderService:
    return OrderService(uow, events)


def get_product_service(uow: UnitOfWork = Depends(get_uow),
                        cache: Cache = Depends(get_cache)) -> ProductService:
    return ProductService(uow, cache)


def get_rate_limiter() -> SlidingWindowRateLimiter:
    settings = get_settings()
    return SlidingWindowRateLimiter(get_redis(), settings.rate_limit, settings.rate_limit_window)


def get_health_checks() -> dict[str, Callable[[], None]]:
    settings = get_settings()
    return {
        "database": lambda: check_database(get_session_factory()),
        "redis": lambda: check_redis(settings.redis_url),
        "rabbitmq": lambda: check_rabbitmq(settings.rabbitmq_url),
    }
