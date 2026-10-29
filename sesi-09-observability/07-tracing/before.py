"""Distributed Tracing - BEFORE (hanya total waktu)

Request POST /orders melewati beberapa langkah: cek stok, simpan ke database, kirim event ke RabbitMQ.
Lalu consumer notifikasi (proses lain) mengirim email dari event itu.
Log hanya mencatat total waktu, jadi saat request lambat kita tidak tahu langkah mana penyebabnya.
Log consumer juga tidak tersambung dengan request yang memicunya.

Jalankan: python before.py
"""
import json
import time

QUEUE = []                           # anggap: queue RabbitMQ


def check_stock():
    time.sleep(0.02)


def save_order():
    time.sleep(0.05)


def publish_event(event: dict):
    time.sleep(0.4)                  # broker sedang lambat
    QUEUE.append(json.dumps(event))


def place_order():
    start = time.perf_counter()
    check_stock()
    save_order()
    publish_event({"type": "order.placed", "order_id": 7})
    ms = (time.perf_counter() - start) * 1000
    print(f"[api]      POST /orders selesai dalam {ms:.0f} ms")


def consume():                       # anggap: proses consumer
    event = json.loads(QUEUE.pop(0))
    time.sleep(0.1)
    print(f"[consumer] email order {event['order_id']} terkirim")


if __name__ == "__main__":
    place_order()
    consume()
