"""Idempotent Consumer - AFTER

Setiap event punya event_id unik yang dibuat producer.
Consumer mencatat event_id di tabel processed_events (primary key, jadi tidak bisa dobel)
dalam SATU transaksi dengan perubahan datanya:
- event_id belum ada : catat + tambah poin, commit bersama
- event_id sudah ada : INSERT gagal (IntegrityError), seluruh transaksi batal, event di-skip lalu di-ack
Pesan boleh datang berapa kali pun, hasilnya tetap sama seperti diproses sekali.

Butuh RabbitMQ: docker compose up -d (dari folder sesi-08)
Jalankan: python after.py
"""
import json
import os
import sqlite3
import uuid

import pika

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE points (customer TEXT PRIMARY KEY, total INTEGER)")
db.execute("INSERT INTO points VALUES ('budi@mail.com', 0)")
ADD_POINTS = "UPDATE points SET total = total + ? WHERE customer = ?"
db.execute("CREATE TABLE processed_events (event_id TEXT PRIMARY KEY)")


def add_points(event):
    try:
        with db:                                 # satu transaksi
            db.execute("INSERT INTO processed_events VALUES (?)",
                       (event["event_id"],))
            db.execute(ADD_POINTS, (event["points"], event["customer"]))
        print(f"  +{event['points']} poin untuk {event['customer']}")
    except sqlite3.IntegrityError:
        print(f"  event {event['event_id'][:8]} sudah diproses, skip")


def run_consumer(crash_before_ack=False):
    with pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL)) as connection:
        channel = connection.channel()
        for method, properties, body in channel.consume("points", inactivity_timeout=1):
            if method is None:
                break
            add_points(json.loads(body))
            if crash_before_ack:
                raise RuntimeError("worker crash sebelum ack")
            channel.basic_ack(method.delivery_tag)


def publish_event():
    with pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL)) as connection:
        channel = connection.channel()
        channel.confirm_delivery()
        channel.queue_delete("points")
        channel.queue_declare("points", durable=True)
        event = {"event_id": str(uuid.uuid4()), "type": "order.paid",
                 "order_id": 1, "customer": "budi@mail.com", "points": 90}
        channel.basic_publish("", "points", json.dumps(event))


if __name__ == "__main__":
    publish_event()
    try:
        run_consumer(crash_before_ack=True)
    except RuntimeError as exc:
        print(f"  CRASH: {exc}")
    print("Consumer dijalankan ulang:")
    run_consumer()

    total = db.execute("SELECT total FROM points WHERE customer = 'budi@mail.com'").fetchone()[0]
    print(f"Total poin budi@mail.com: {total} (seharusnya 90)")
