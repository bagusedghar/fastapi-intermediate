"""Test task Celery (mode eager): retry, idempotency, dan kegagalan permanen."""
import pytest

from app.infrastructure.notifiers import NotificationServiceDown
from app.worker import tasks
from app.worker.jobs import get_job_status


class FlakyNotifier:
    """Gagal sebanyak `failures` kali, setelah itu berhasil."""

    def __init__(self, failures: int = 0):
        self.failures = failures
        self.sent: list[tuple[str, str]] = []

    def send(self, to: str, message: str) -> None:
        if self.failures:
            self.failures -= 1
            raise NotificationServiceDown("Server email timeout")
        self.sent.append((to, message))


@pytest.fixture
def notifier(monkeypatch):
    def use(failures: int = 0) -> FlakyNotifier:
        fake = FlakyNotifier(failures)
        monkeypatch.setattr(tasks, "create_notifier", lambda *args: fake)
        return fake
    return use


def test_retry_sampai_berhasil(notifier):
    fake = notifier(failures=2)
    result = tasks.send_notification.delay("key-1", "budi@mail.com", "Order #1 berhasil")
    assert result.state == "SUCCESS"
    assert fake.sent == [("budi@mail.com", "Order #1 berhasil")]


def test_notifikasi_yang_sama_hanya_dikirim_sekali(notifier):
    fake = notifier()
    first = tasks.send_notification.delay("key-1", "budi@mail.com", "Order #1 berhasil")
    second = tasks.send_notification.delay("key-1", "budi@mail.com", "Order #1 berhasil")
    assert (first.result, second.result) == ("sent", "skipped")
    assert len(fake.sent) == 1


def test_gagal_permanen_setelah_max_retries(notifier):
    fake = notifier(failures=10)
    result = tasks.send_notification.delay("key-1", "budi@mail.com", "Order #1 berhasil")

    status = get_job_status(result.id)
    assert status["status"] == "failed"
    assert status["error"] == "Server email timeout"
    assert fake.sent == []
