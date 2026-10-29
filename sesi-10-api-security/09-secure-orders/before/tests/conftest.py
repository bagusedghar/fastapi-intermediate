"""Setting test: tanpa Redis, RabbitMQ, worker, maupun database sungguhan.

- Celery mode eager, database SQLite di memory
- Redis diganti fakeredis (Redis palsu di memory, perintahnya sama)
- Publisher RabbitMQ diganti FakeEventPublisher, event yang diumumkan bisa dicek di test
- Trace tidak dikirim ke Jaeger (TRACING_ENABLED=0)
Environment di-set sebelum app di-import, karena config dibaca saat import.
"""
import os

os.environ.update(
    DATABASE_URL="sqlite://",
    CELERY_TASK_ALWAYS_EAGER="1",
    CELERY_BROKER_URL="memory://",
    CELERY_RESULT_BACKEND="cache+memory://",
    NOTIFICATION_FAIL_RATE="0",
    RATE_LIMIT="20",
    TRACING_ENABLED="0",
)

import fakeredis  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.api.dependencies import get_event_publisher  # noqa: E402
from app.infrastructure import redis_client  # noqa: E402
from app.infrastructure.database import get_session_factory  # noqa: E402
from app.main import app  # noqa: E402
from tests.fakes import FakeEventPublisher  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_database():
    get_session_factory.cache_clear()          # setiap test dapat database baru
    yield
    get_session_factory.cache_clear()


@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(redis_client.Redis, "from_url", lambda *args, **kwargs: fake)
    redis_client.get_redis.cache_clear()       # setiap test dapat Redis baru yang kosong
    yield fake
    redis_client.get_redis.cache_clear()


@pytest.fixture(autouse=True)
def events():
    fake = FakeEventPublisher()
    app.dependency_overrides[get_event_publisher] = lambda: fake
    yield fake
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    client = TestClient(app)
    client.post("/products", json={"name": "Keyboard", "price": 500_000, "stock": 5})
    client.post("/products", json={"name": "Mouse", "price": 100_000, "stock": 1})
    return client


def order(*items, customer_type="vip"):
    return {"customer": "budi@mail.com", "customer_type": customer_type,
            "items": [{"product_id": p, "qty": q} for p, q in items]}
