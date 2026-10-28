"""Infrastructure: RabbitMQ (topologi + adapter port EventPublisher).

Topologi:
    exchange "orders" (topic) --order.*--> notifications
    notifications        --nack(requeue=False)-->  notifications.dlq
    notifications.retry  --setelah expiration--->  notifications (dicoba lagi)
    exchange "orders" (topic) --order.paid--> points
    points               --nack(requeue=False)-->  points.dlq

declare_topology dipanggil oleh publisher dan consumer. Deklarasi bersifat idempotent,
jadi urutan menjalankan API dan consumer tidak penting, dan event tidak hilang karena queue belum ada.
"""
import json
import logging

import pika

EXCHANGE = "orders"
QUEUE = "notifications"
RETRY_QUEUE = "notifications.retry"
DEAD_LETTER_QUEUE = "notifications.dlq"
POINTS_QUEUE = "points"
POINTS_DEAD_LETTER_QUEUE = "points.dlq"

logger = logging.getLogger("app.events")


def connect(url: str) -> pika.BlockingConnection:
    return pika.BlockingConnection(pika.URLParameters(url))


def declare_topology(channel) -> None:
    channel.exchange_declare(EXCHANGE, exchange_type="topic", durable=True)
    channel.queue_declare(DEAD_LETTER_QUEUE, durable=True)
    channel.queue_declare(QUEUE, durable=True, arguments={
        "x-dead-letter-exchange": "", "x-dead-letter-routing-key": DEAD_LETTER_QUEUE})
    channel.queue_bind(QUEUE, EXCHANGE, routing_key="order.*")
    channel.queue_declare(RETRY_QUEUE, durable=True, arguments={
        "x-dead-letter-exchange": "", "x-dead-letter-routing-key": QUEUE})
    channel.queue_declare(POINTS_DEAD_LETTER_QUEUE, durable=True)
    channel.queue_declare(POINTS_QUEUE, durable=True, arguments={
        "x-dead-letter-exchange": "", "x-dead-letter-routing-key": POINTS_DEAD_LETTER_QUEUE})
    channel.queue_bind(POINTS_QUEUE, EXCHANGE, routing_key="order.paid")


class RabbitMQPublisher:
    """Satu koneksi per publish supaya sederhana. Di traffic tinggi, koneksi sebaiknya dipakai ulang."""

    def __init__(self, url: str):
        self.url = url

    def publish(self, event: dict) -> None:
        try:
            with connect(self.url) as connection:
                channel = connection.channel()
                channel.confirm_delivery()                  # tunggu RabbitMQ konfirmasi pesan diterima
                declare_topology(channel)
                channel.basic_publish(EXCHANGE, event["type"], json.dumps(event), pika.BasicProperties(
                    content_type="application/json", message_id=event["event_id"],
                    delivery_mode=pika.DeliveryMode.Persistent))
        except pika.exceptions.AMQPError:
            # order sudah ter-commit, jadi request tidak digagalkan. Event-nya hilang dan tercatat di log.
            logger.exception("Gagal publish event %s %s", event["type"], event["event_id"])
