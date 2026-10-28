"""Consumer: tambah poin loyalty dari event order.paid di queue "points".

Queue "points" di-bind ke exchange "orders" dengan routing key "order.paid",
jadi consumer ini hanya menerima event pembayaran. Consumer notifikasi tetap berjalan seperti biasa.
- Berhasil / sudah pernah diproses : ack
- Pesan rusak (InvalidEvent)       : nack(requeue=False) -> points.dlq
Database mati atau error lain: consumer berhenti tanpa ack, pesan tetap di queue dan diproses lagi
saat consumer dijalankan ulang.

Jalankan dari folder after/:
    python -m app.consumers.points_consumer
"""
import json
import logging

from app.application.errors import InvalidEvent
from app.application.points_service import PointsService
from app.infrastructure.config import get_settings
from app.infrastructure.database import get_session_factory
from app.infrastructure.points_ledger import SqlAlchemyPointsLedger
from app.infrastructure.rabbitmq import POINTS_QUEUE, connect, declare_topology

logger = logging.getLogger("app.consumers.points")


def process_message(channel, method, body: bytes, service: PointsService) -> str:
    try:
        result = service.handle(json.loads(body))
    except (ValueError, InvalidEvent) as exc:                 # JSON rusak atau isi event salah
        logger.error("Pesan rusak, dipindah ke DLQ: %s", exc)
        channel.basic_nack(method.delivery_tag, requeue=False)
        return "dead_lettered"
    channel.basic_ack(method.delivery_tag)
    return result


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.getLogger("pika").setLevel(logging.WARNING)
    service = PointsService(SqlAlchemyPointsLedger(get_session_factory()))

    with connect(get_settings().rabbitmq_url) as connection:
        channel = connection.channel()
        declare_topology(channel)
        channel.basic_qos(prefetch_count=1)
        logger.info("Menunggu event di queue %s ...", POINTS_QUEUE)
        for method, properties, body in channel.consume(POINTS_QUEUE):
            result = process_message(channel, method, body, service)
            logger.info("event %s: %s", properties.message_id, result)


if __name__ == "__main__":
    main()
