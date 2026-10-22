"""Worker: task Celery.

Task adalah pintu masuk seperti route di api/: menerima job, memanggil use case atau adapter, selesai.
- send_notification     : retry dengan backoff, idempotent lewat idempotency key
- generate_sales_report : bisa lama, dibatasi time limit
Semua task memakai AlertingTask, jadi retry dan kegagalan permanen selalu tercatat di log worker.
"""
import time

from celery import Task
from celery.utils.log import get_task_logger

from app.application.report_service import ReportService
from app.infrastructure.config import get_settings
from app.infrastructure.database import get_session_factory
from app.infrastructure.notification_log import SqlAlchemyNotificationLog
from app.infrastructure.notifiers import NotificationServiceDown, create_notifier
from app.infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from app.worker.celery_app import celery_app

logger = get_task_logger(__name__)


class AlertingTask(Task):
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        logger.warning("%s retry ke-%s: %s", self.name, self.request.retries + 1, exc)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # di aplikasi nyata: kirim alert ke Slack/Sentry atau simpan ke tabel failed_jobs
        logger.error("[ALERT] %s gagal permanen (task_id=%s, args=%s): %s", self.name, task_id, args, exc)


@celery_app.task(base=AlertingTask, autoretry_for=(NotificationServiceDown,), retry_backoff=True,
                 max_retries=3, soft_time_limit=30, time_limit=60)
def send_notification(key: str, to: str, message: str) -> str:
    settings = get_settings()
    log = SqlAlchemyNotificationLog(get_session_factory())
    if log.already_sent(key):
        return "skipped"

    create_notifier(settings.notification_channel, settings.notification_fail_rate).send(to, message)
    log.mark_sent(key)
    return "sent"


@celery_app.task(base=AlertingTask, soft_time_limit=120, time_limit=150)
def generate_sales_report() -> dict:
    time.sleep(get_settings().report_delay)       # simulasi query & perhitungan yang lama
    return ReportService(SqlAlchemyUnitOfWork(get_session_factory())).sales_summary()
