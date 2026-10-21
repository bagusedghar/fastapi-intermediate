"""Failure Handling - AFTER

- Error dibiarkan naik, supaya Celery bisa retry dan mencatat status FAILURE
- Base class AlertingTask: on_retry dan on_failure dipanggil Celery otomatis
- Task yang gagal permanen dicatat di FAILED_JOBS, lengkap dengan argumen untuk dijalankan ulang

Di aplikasi nyata FAILED_JOBS bisa berupa tabel failed_jobs, alert Slack, atau Sentry.

Jalankan demo: python after.py
"""
from celery import Celery, Task

celery_app = Celery("demo", broker="redis://localhost:6379/0", backend="redis://localhost:6379/1")

FAILED_JOBS: list[dict] = []


class EmailServiceDown(Exception):
    pass


class AlertingTask(Task):
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        print(f"[RETRY] {self.name} retry ke-{self.request.retries + 1}: {exc}")

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        FAILED_JOBS.append({"task": self.name, "task_id": task_id, "args": args, "error": str(exc)})
        print(f"[ALERT] {self.name} gagal permanen: {exc}")


def send_email(to: str, message: str) -> None:
    raise EmailServiceDown("Server email tidak bisa dihubungi")


@celery_app.task(base=AlertingTask, autoretry_for=(EmailServiceDown,), retry_backoff=True, max_retries=3)
def send_order_email(to: str, message: str) -> None:
    send_email(to, message)           # tanpa try/except


if __name__ == "__main__":
    celery_app.conf.task_always_eager = True
    result = send_order_email.delay("budi@mail.com", "Order #1 berhasil")
    print("Status:", result.state)    # FAILURE
    print("Failed jobs:", FAILED_JOBS)
