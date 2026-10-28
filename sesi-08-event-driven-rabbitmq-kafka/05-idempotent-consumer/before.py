"""Idempotent Consumer - BEFORE

Ack manual menjamin pesan tidak hilang (at-least-once), tapi konsekuensinya pesan bisa diterima dua kali.
Contoh: poin sudah ditambahkan, lalu consumer crash sebelum sempat ack.
Pesan dikirim ulang, poin ditambahkan lagi. Customer mendapat poin dua kali.

Database poin memakai SQLite di memory supaya demo tidak butuh setup tambahan.

Butuh RabbitMQ: docker compose up -d (dari folder sesi-08)
Jalankan: python before.py
"""
import json
import os
import sqlite3
import uuid

import pika

URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE points (customer TEXT PRIMARY KEY, total INT)")
db.execute("INSERT INTO points VALUES ('budi@mail.com', 0)")
ADD_POINTS = "UPDATE points SET total = total + ? WHERE customer = ?"


def add_points(event):
    with db:
        db.execute(ADD_POINTS, (event["points"], event["customer"]))
    print(f"  +{event['points']} poin untuk {event['customer']}")


def run_consumer(crash_before_ack=False):
    with pika.BlockingConnection(pika.URLParameters(URL)) as conn:
        channel = conn.channel()
        for method, properties, body in channel.consume(
                "points", inactivity_timeout=1):
            if method is None:
                break
            add_points(json.loads(body))
            if crash_before_ack:
                raise RuntimeError("worker crash sebelum ack")
            channel.basic_ack(method.delivery_tag)


def publish_event():
    with pika.BlockingConnection(pika.URLParameters(URL)) as conn:
        channel = conn.channel()
        channel.confirm_delivery()
        channel.queue_delete("points")
        channel.queue_declare("points", durable=True)
        event = {"event_id": str(uuid.uuid4()), "type": "order.paid",
                 "order_id": 1, "customer": "budi@mail.com",
                 "points": 90}
        channel.basic_publish("", "points", json.dumps(event))


if __name__ == "__main__":
    publish_event()
    try:
        run_consumer(crash_before_ack=True)
    except RuntimeError as exc:
        print(f"  CRASH: {exc}")
    print("Consumer dijalankan ulang:")
    run_consumer()

    total = db.execute("SELECT total FROM points").fetchone()[0]
    print(f"Total poin budi@mail.com: {total} (seharusnya 90)")
