"""Kafka Basics - BEFORE (RabbitMQ: pesan dihapus setelah di-ack)

RabbitMQ cocok sebagai queue job: pesan diambil, dikerjakan, di-ack, lalu hilang dari queue.
Tapi ada kebutuhan yang tidak bisa dipenuhi:
- Tim analytics baru bergabung dan butuh semua event lama. Queue mereka baru dibuat, isinya kosong
- Ada bug di consumer email, ingin memproses ulang event kemarin. Event-nya sudah tidak ada

Butuh RabbitMQ: docker compose up -d (dari folder sesi-08)
Jalankan: python before.py
"""
import json
import os

import pika

URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")


def consume(channel, queue) -> int:
    received = 0
    for method, properties, body in channel.consume(
            queue, inactivity_timeout=1):
        if method is None:
            break
        channel.basic_ack(method.delivery_tag)
        received += 1
    channel.cancel()
    return received


def declare(channel, queue):
    channel.queue_declare(queue, durable=True)
    channel.queue_bind(queue, "orders", routing_key="#")


if __name__ == "__main__":
    with pika.BlockingConnection(pika.URLParameters(URL)) as conn:
        channel = conn.channel()
        channel.confirm_delivery()
        channel.exchange_declare("orders", exchange_type="topic",
                                 durable=True)
        for queue in ("email", "analytics"):
            channel.queue_delete(queue)        # mulai dari kosong
        declare(channel, "email")

        for order_id in range(1, 7):
            event = {"type": "order.placed", "order_id": order_id}
            channel.basic_publish("orders", "order.placed",
                                  json.dumps(event))

        print(f"Consumer email           : "
              f"{consume(channel, 'email')} event")
        print(f"Consumer email baca ulang: "
              f"{consume(channel, 'email')} event")

        declare(channel, "analytics")   # tim analytics baru bergabung
        print(f"Consumer analytics (baru): "
              f"{consume(channel, 'analytics')} event")
