"""Exchange & Queue - AFTER (topic exchange + binding)

Producer cukup kirim ke exchange "orders" dengan routing key sesuai jenis event (order.placed, order.paid).
Setiap consumer punya queue sendiri dan memilih event yang dia mau lewat binding:
    *  = tepat satu kata      order.*  -> order.placed, order.paid, order.cancelled
    #  = nol kata atau lebih  #        -> semua event
Consumer baru = queue + binding baru. Kode producer tidak berubah.

durable=True dan delivery_mode Persistent: exchange, queue, dan pesan tetap ada setelah RabbitMQ restart.
Biasanya consumer yang mendeklarasikan queue dan binding miliknya. Di demo ini dibuat di satu file.

Butuh RabbitMQ: docker compose up -d (dari folder sesi-08)
Jalankan: python after.py
"""
import json
import os

import pika

URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

BINDINGS = {"email": "order.*",
            "points": "order.paid",
            "analytics": "#"}
PERSISTENT = pika.BasicProperties(
    delivery_mode=pika.DeliveryMode.Persistent)


def publish(channel, event: dict):
    channel.basic_publish(exchange="orders",
                          routing_key=event["type"],
                          body=json.dumps(event),
                          properties=PERSISTENT)


if __name__ == "__main__":
    with pika.BlockingConnection(pika.URLParameters(URL)) as conn:
        channel = conn.channel()
        channel.confirm_delivery()    # tunggu konfirmasi RabbitMQ
        channel.exchange_declare("orders", exchange_type="topic",
                                 durable=True)
        for queue, pattern in BINDINGS.items():
            channel.queue_delete(queue)        # mulai dari kosong
            channel.queue_declare(queue, durable=True)
            channel.queue_bind(queue, "orders", routing_key=pattern)

        publish(channel, {"type": "order.placed", "order_id": 1})
        publish(channel, {"type": "order.paid", "order_id": 1})

        for queue, pattern in BINDINGS.items():
            info = channel.queue_declare(queue, passive=True)
            count = info.method.message_count
            print(f"Queue {queue:<9} ({pattern:<10}): {count} pesan")
