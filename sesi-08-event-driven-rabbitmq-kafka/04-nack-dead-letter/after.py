"""Nack & Dead Letter Queue - AFTER (retry dengan jeda + DLQ)

Error dibedakan:
- Pesan rusak (ValueError)        : dicoba lagi pun tetap gagal -> nack(requeue=False) -> langsung ke DLQ
- Gangguan sementara (server down) : retry dengan jeda 0.5 s, 1 s, 2 s. Lewat MAX_RETRIES -> DLQ

Tiga queue:
- email        : queue utama. Pesan yang di-nack(requeue=False) dipindahkan ke email.dlq (x-dead-letter-*)
- email.retry  : ruang tunggu. Pesan diberi expiration (jeda), setelah kedaluwarsa kembali ke email
- email.dlq    : dead letter queue, dicek manual lewat dashboard RabbitMQ, lalu diperbaiki atau dikirim ulang

Jumlah retry disimpan di header pesan (x-retries).

Butuh RabbitMQ: docker compose up -d (dari folder sesi-08)
Jalankan: python after.py
"""
import json
import os
from collections import Counter

import pika

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
MAX_RETRIES = 3

attempts = Counter()


class EmailServerDown(Exception):
    """Gangguan sementara, bisa berhasil kalau dicoba lagi."""


def send_email(event):
    order_id = event["order_id"]
    attempts[order_id] += 1
    if not event["customer"]:
        raise ValueError("customer kosong")
    if order_id == 2 and attempts[order_id] <= 2:
        raise EmailServerDown("server email timeout")
    print(f"  email order #{order_id} terkirim (percobaan ke-{attempts[order_id]})")


def declare_queues(channel):
    channel.queue_declare("email.dlq", durable=True)
    channel.queue_declare("email", durable=True, arguments={
        "x-dead-letter-exchange": "", "x-dead-letter-routing-key": "email.dlq"})
    channel.queue_declare("email.retry", durable=True, arguments={
        "x-dead-letter-exchange": "", "x-dead-letter-routing-key": "email"})


def handle(channel, method, properties, body):
    retries = (properties.headers or {}).get("x-retries", 0)
    try:
        send_email(json.loads(body))
        channel.basic_ack(method.delivery_tag)
    except ValueError as exc:                    # pesan rusak
        print(f"  pesan rusak ({exc}) -> DLQ")
        channel.basic_nack(method.delivery_tag, requeue=False)
    except EmailServerDown as exc:
        if retries >= MAX_RETRIES:
            print(f"  gagal {retries + 1}x ({exc}) -> DLQ")
            channel.basic_nack(method.delivery_tag, requeue=False)
            return
        delay_ms = 500 * 2 ** retries
        props = pika.BasicProperties(headers={"x-retries": retries + 1},
                                     expiration=str(delay_ms))
        channel.basic_publish("", "email.retry", body, props)
        channel.basic_ack(method.delivery_tag)
        print(f"  {exc}, retry ke-{retries + 1} dalam {delay_ms} ms")


if __name__ == "__main__":
    with pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL)) as connection:
        channel = connection.channel()
        channel.confirm_delivery()
        for queue in ("email", "email.retry", "email.dlq"):
            channel.queue_delete(queue)                            # mulai dari queue kosong
        declare_queues(channel)
        channel.basic_publish("", "email", json.dumps({"order_id": 1, "customer": ""}))   # pesan rusak
        channel.basic_publish("", "email", json.dumps({"order_id": 2, "customer": "budi@mail.com"}))

        channel.basic_qos(prefetch_count=1)
        for method, properties, body in channel.consume("email", inactivity_timeout=3):
            if method is None:
                break
            handle(channel, method, properties, body)

        for order_id in (1, 2):
            print(f"Order #{order_id}: diproses {attempts[order_id]} kali")
        dlq = channel.queue_declare("email.dlq", passive=True).method.message_count
        print(f"Isi email.dlq: {dlq} pesan")
