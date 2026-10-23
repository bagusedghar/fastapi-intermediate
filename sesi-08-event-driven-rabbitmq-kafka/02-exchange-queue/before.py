"""Exchange & Queue - BEFORE (producer kirim langsung ke queue)

Producer memakai default exchange (""), jadi routing_key = nama queue tujuan.
Akibatnya producer harus tahu semua consumer yang ada:
- Ada consumer baru (analytics) = kode producer diubah
- Consumer yang cuma butuh event tertentu (points hanya order.paid) tetap harus diatur di producer

Butuh RabbitMQ: docker compose up -d (dari folder sesi-08)
Jalankan: python before.py
"""
import json
import os

import pika

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

QUEUES = ["email", "points"]          # consumer baru = tambah di sini


def publish(channel, event: dict):
    for queue in QUEUES:
        if queue == "points" and event["type"] != "order.paid":
            continue    # aturan consumer, ditulis di producer
        channel.basic_publish(exchange="", routing_key=queue,
                              body=json.dumps(event))


if __name__ == "__main__":
    with pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL)) as connection:
        channel = connection.channel()
        channel.confirm_delivery()                        # publish menunggu konfirmasi dari RabbitMQ
        for queue in QUEUES:
            channel.queue_delete(queue)                   # mulai dari queue kosong
            channel.queue_declare(queue, durable=True)

        publish(channel, {"type": "order.placed", "order_id": 1})
        publish(channel, {"type": "order.paid", "order_id": 1})

        for queue in QUEUES:
            count = channel.queue_declare(queue, passive=True).method.message_count
            print(f"Queue {queue:<9}: {count} pesan")
