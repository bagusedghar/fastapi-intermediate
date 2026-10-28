"""Infrastructure: koneksi database SQLAlchemy.

get_session_factory() dipakai bersama oleh API dan worker Celery.
"""
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


def create_session_factory(database_url: str) -> sessionmaker:
    from app.infrastructure import models  # noqa: F401  (daftarkan tabel ke Base)

    options = {}
    if database_url.startswith("sqlite"):
        options["connect_args"] = {"check_same_thread": False}
    if database_url == "sqlite://":          # database di memory, dipakai di test
        options["poolclass"] = StaticPool

    engine = create_engine(database_url, **options)
    Base.metadata.create_all(engine)
    return sessionmaker(engine, expire_on_commit=False)


@lru_cache
def get_session_factory() -> sessionmaker:
    from app.infrastructure.config import get_settings

    return create_session_factory(get_settings().database_url)
