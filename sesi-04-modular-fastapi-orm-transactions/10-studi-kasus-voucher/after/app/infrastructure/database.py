"""Infrastructure: koneksi database SQLAlchemy."""
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
