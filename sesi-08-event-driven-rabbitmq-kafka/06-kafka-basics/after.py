"""Kafka Basics - AFTER (topic, partition, consumer group, offset)

Kafka menyimpan event seperti log yang hanya ditambah di belakang. Event TIDAK dihapus setelah dibaca,
baru dihapus setelah masa simpan habis (retention, default 7 hari).
- Topic           : nama log-nya, misalnya "orders"
- Partition       : topic dipecah jadi beberapa bagian supaya bisa dibaca paralel.
                    Event dengan key yang sama (customer) selalu masuk partition yang sama, jadi urutannya terjaga
- Offset          : nomor urut event di dalam partition
- Consumer group  : satu tim pembaca. Kafka mencatat offset terakhir per group (commit),
                    jadi group yang sudah membaca lanjut dari posisinya, group baru mulai dari awal
                    (auto.offset.reset = earliest)

Butuh Kafka: docker compose up -d (dari folder sesi-08)
Jalankan: python after.py
"""
import json
import os
import time
from collections import defaultdict

from confluent_kafka import Consumer, Producer
from confluent_kafka.admin import AdminClient, NewTopic

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
TOPIC = "orders"

EVENTS = [(1, "budi"), (2, "ani"), (3, "budi"), (4, "siti"), (5, "ani"), (6, "budi")]


def create_topic():
    admin = AdminClient({"bootstrap.servers": BOOTSTRAP})
    if TOPIC in admin.list_topics(timeout=10).topics:      # mulai dari topic kosong
        admin.delete_topics([TOPIC])[TOPIC].result()
        while TOPIC in admin.list_topics(timeout=10).topics:
            time.sleep(0.5)
    admin.create_topics([NewTopic(TOPIC, num_partitions=3)])[TOPIC].result()


def publish():
    producer = Producer({"bootstrap.servers": BOOTSTRAP,
                         "partitioner": "murmur2_random"})     # cara hitung partition sama dengan client Java
    for order_id, customer in EVENTS:
        event = {"type": "order.placed", "order_id": order_id, "customer": customer}
        # key menentukan partition: customer sama = partition sama
        producer.produce(TOPIC, key=customer, value=json.dumps(event))
    producer.flush()


def consume(group_id: str) -> dict:
    consumer = Consumer({"bootstrap.servers": BOOTSTRAP, "group.id": group_id,
                         "auto.offset.reset": "earliest",
                         "enable.auto.commit": False})
    consumer.subscribe([TOPIC])
    received = defaultdict(list)
    idle = 0
    while idle < 2:                                           # demo: berhenti kalau 2 detik tidak ada event
        msg = consumer.poll(1.0)
        if msg is None:
            idle += 1 if consumer.assignment() else 0
            continue
        event = json.loads(msg.value())
        received[msg.partition()].append((msg.offset(), f"#{event['order_id']} {event['customer']}"))
        consumer.commit(msg)         # catat: group ini sudah baca sampai sini
    consumer.close()
    return received


def show(label: str, received: dict):
    print(f"{label}: {sum(len(v) for v in received.values())} event")
    for partition, rows in sorted(received.items()):
        offsets = ",".join(str(offset) for offset, _ in rows)
        orders = ", ".join(order for _, order in rows)
        print(f"  partition {partition}, offset {offsets}: {orders}")


if __name__ == "__main__":
    create_topic()
    publish()
    show("Consumer group email           ", consume("email"))
    show("Consumer group email baca ulang", consume("email"))
    show("Consumer group analytics (baru)", consume("analytics"))
