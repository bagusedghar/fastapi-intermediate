"""Consumer: kirim notifikasi dari event order di queue "notifications".

Consumer adalah pintu masuk seperti route di api/ dan task di worker/:
menerima pesan, memanggil use case (NotificationService), lalu memutuskan ack/nack.
- Berhasil / sudah pernah dikirim   : ack
- Pesan rusak (InvalidEvent)        : nack(requeue=False) -> langsung ke DLQ, tidak di-retry
- Server notifikasi gangguan        : retry dengan jeda (1 s, 2 s, 4 s), lewat batas -> DLQ
Ack dikirim setelah pekerjaan selesai, jadi consumer crash = pesan dikirim ulang, bukan hilang.

Jalankan dari folder after/:
    python -m app.consumers.notification_consumer
"""
import json
import logging

import pika

from app.application.errors import InvalidEvent
from app.application.notification_service import NotificationService
from app.infrastructure.config import get_settings
from app.infrastructure.database import get_session_factory
from app.infrastructure.notification_log import SqlAlchemyNotificationLog
from app.infrastructure.notifiers import NotificationServiceDown, create_notifier
from app.infrastructure.rabbitmq import QUEUE, RETRY_QUEUE, connect, declare_topology

logger = logging.getLogger("app.consumers.notification")


def process_message(channel, method, properties, body: bytes, service: NotificationService,
                    max_retries: int, retry_delay_ms: int) -> str:
    retries = (properties.headers or {}).get("x-retries", 0)
    try:
        result = service.handle(json.loads(body))
        channel.basic_ack(method.delivery_tag)
        return result
    except (ValueError, InvalidEvent) as exc:                 # JSON rusak atau isi event salah
        logger.error("Pesan rusak, dipindah ke DLQ: %s", exc)
        channel.basic_nack(method.delivery_tag, requeue=False)
        return "dead_lettered"
    except NotificationServiceDown as exc:
        if retries >= max_retries:
            logger.error("[ALERT] Gagal %s kali, dipindah ke DLQ: %s", retries + 1, exc)
            channel.basic_nack(method.delivery_tag, requeue=False)
            return "dead_lettered"
        delay_ms = retry_delay_ms * 2 ** retries
        channel.basic_publish("", RETRY_QUEUE, body, pika.BasicProperties(
            content_type="application/json", message_id=properties.message_id,
            headers={"x-retries": retries + 1}, expiration=str(delay_ms),
            delivery_mode=pika.DeliveryMode.Persistent))
        channel.basic_ack(method.delivery_tag)
        logger.warning("%s, retry ke-%s dalam %s ms", exc, retries + 1, delay_ms)
        return "retrying"


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.getLogger("pika").setLevel(logging.WARNING)
    settings = get_settings()
    service = NotificationService(
        create_notifier(settings.notification_channel, settings.notification_fail_rate),
        SqlAlchemyNotificationLog(get_session_factory()))

    with connect(settings.rabbitmq_url) as connection:
        channel = connection.channel()
        declare_topology(channel)
        channel.basic_qos(prefetch_count=1)                   # pegang 1 pesan yang belum di-ack
        logger.info("Menunggu event di queue %s ...", QUEUE)
        for method, properties, body in channel.consume(QUEUE):
            result = process_message(channel, method, properties, body, service,
                                     settings.notification_max_retries, settings.notification_retry_delay_ms)
            logger.info("event %s: %s", properties.message_id, result)


if __name__ == "__main__":
    main()
