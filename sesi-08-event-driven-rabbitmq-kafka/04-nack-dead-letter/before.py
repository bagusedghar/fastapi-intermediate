"""Nack & Dead Letter Queue - BEFORE (nack requeue=True untuk semua error)

Setiap error, pesan dikembalikan ke queue (basic_nack requeue=True) supaya dicoba lagi.
- Pesan rusak (customer kosong) tidak akan pernah berhasil, jadi berputar terus tanpa henti
- Tidak ada jeda: server email yang sedang error langsung dikirimi request lagi
- Pesan di belakangnya ikut tertunda

Butuh RabbitMQ: docker compose up -d (dari folder sesi-08)
Jalankan: python before.py
"""
import json
import os
import time
from collections import Counter

import pika

URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

attempts = Counter()


class EmailServerDown(Exception):
    """Error sementara, bisa berhasil jika dicoba lagi."""


def send_email(event):
    order_id = event["order_id"]
    attempts[order_id] += 1
    if not event["customer"]:
        raise ValueError("customer kosong")
    if order_id == 2 and attempts[order_id] <= 2:
        raise EmailServerDown("server email timeout")
    print(f"  email order #{order_id} terkirim "
          f"(percobaan ke-{attempts[order_id]})")


def handle(channel, method, body):
    try:
        send_email(json.loads(body))
        channel.basic_ack(method.delivery_tag)
    except (ValueError, EmailServerDown):
        # kembalikan ke queue, coba lagi
        channel.basic_nack(method.delivery_tag, requeue=True)


if __name__ == "__main__":
    with pika.BlockingConnection(pika.URLParameters(URL)) as conn:
        channel = conn.channel()
        channel.confirm_delivery()
        channel.queue_delete("email")
        channel.queue_declare("email", durable=True)
        for event in ({"order_id": 1, "customer": ""},  # pesan rusak
                      {"order_id": 2, "customer": "budi@mail.com"}):
            channel.basic_publish("", "email", json.dumps(event))

        channel.basic_qos(prefetch_count=1)
        stop_at = time.monotonic() + 3  # demo: berhenti setelah 3 s
        for method, properties, body in channel.consume(
                "email", inactivity_timeout=1):
            if method is None or time.monotonic() > stop_at:
                break
            handle(channel, method, body)

    for order_id in (1, 2):
        print(f"Order #{order_id}: diproses "
              f"{attempts[order_id]:,} kali")
