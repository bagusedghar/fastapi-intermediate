"""Setting test: Celery mode eager (tanpa Redis & worker), database SQLite di memory.

Environment di-set sebelum app di-import, karena config dibaca saat import.
"""
import os

os.environ.update(
    DATABASE_URL="sqlite://",
    CELERY_TASK_ALWAYS_EAGER="1",
    CELERY_BROKER_URL="memory://",
    CELERY_RESULT_BACKEND="cache+memory://",
    NOTIFICATION_FAIL_RATE="0",
    REPORT_DELAY="0",
)

import pytest  # noqa: E402

from app.infrastructure.database import get_session_factory  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_database():
    get_session_factory.cache_clear()          # setiap test dapat database baru
    yield
    get_session_factory.cache_clear()
