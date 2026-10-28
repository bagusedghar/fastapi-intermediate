"""Ack - BEFORE (auto_ack=True)

Dengan auto_ack, RabbitMQ menganggap pesan selesai begitu dikirim ke consumer, lalu menghapusnya.
Kalau consumer crash di tengah jalan, pesan yang sedang diproses (dan yang sudah dikirim ke consumer) hilang.

Butuh RabbitMQ: docker compose up -d (dari folder sesi-08)
Jalankan: python before.py
"""
import json
import os

import pika

URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")


def send_email(event, crash_on=None):
    if event["order_id"] == crash_on:
        raise RuntimeError(f"worker crash saat memproses "
                           f"order #{crash_on}")
    print(f"  email order #{event['order_id']} terkirim")


def run_consumer(crash_on=None) -> int:
    processed = 0
    with pika.BlockingConnection(pika.URLParameters(URL)) as conn:
        channel = conn.channel()
        for method, properties, body in channel.consume(
                "email", auto_ack=True, inactivity_timeout=1):
            if method is None:
                break                 # queue kosong, demo selesai
            send_email(json.loads(body), crash_on)
            processed += 1
    return processed


def publish_orders():
    with pika.BlockingConnection(pika.URLParameters(URL)) as conn:
        channel = conn.channel()
        channel.confirm_delivery()
        channel.queue_delete("email")          # mulai dari kosong
        channel.queue_declare("email", durable=True)
        for order_id in (1, 2, 3):
            body = json.dumps({"order_id": order_id})
            channel.basic_publish("", "email", body)


def count() -> int:
    with pika.BlockingConnection(pika.URLParameters(URL)) as conn:
        info = conn.channel().queue_declare("email", passive=True)
        return info.method.message_count


if __name__ == "__main__":
    publish_orders()
    print(f"Pesan di queue: {count()}")
    try:
        run_consumer(crash_on=2)
    except RuntimeError as exc:
        print(f"  CRASH: {exc}")
    print(f"Sisa di queue setelah crash: {count()}")

    print("Consumer dijalankan ulang:")
    print(f"  {run_consumer()} pesan diproses")
