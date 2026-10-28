"""Sync vs Async - AFTER (producer-consumer)

place_order tetap memanggil reserve_stock secara sync, karena butuh jawabannya saat itu juga.
Sisanya cukup tahu belakangan: place_order menaruh event "order.placed" ke queue lalu langsung selesai.
Consumer mengambil event dari queue dan mengerjakannya di proses terpisah.
- Waktu response hanya untuk simpan order
- Analytics mati tidak membuat order gagal
- Layanan baru cukup ditambahkan di sisi consumer, place_order tidak berubah

Di sini queuenya queue.Queue di memory supaya mudah dilihat.
Di produksi queuenya message broker (RabbitMQ / Kafka), jadi event tetap ada walaupun aplikasi restart.

Jalankan: python after.py
"""
import queue
import threading
import time

events = queue.Queue()


def reserve_stock(order):
    time.sleep(0.05)


def send_email(event):
    time.sleep(0.8)
    print(f"  [email] order #{event['id']} terkirim "
          f"ke {event['customer']}")


def add_points(event):
    time.sleep(0.3)
    points = event["total"] // 10_000
    print(f"  [points] +{points} poin untuk {event['customer']}")


def update_analytics(event):
    raise ConnectionError("analytics service tidak merespons")


def place_order(order):                       # producer
    reserve_stock(order)
    print(f"  [order] order #{order['id']} disimpan")
    # kirim event ke queue, tidak menunggu siapa pun
    events.put({"type": "order.placed", **order})
    return order


HANDLERS = [send_email, add_points, update_analytics]


def consumer():
    while True:
        event = events.get()
        for handler in HANDLERS:
            try:
                handler(event)
            except ConnectionError as exc:
                print(f"  [consumer] {handler.__name__} gagal, "
                      f"dicoba lagi nanti: {exc}")
        events.task_done()


if __name__ == "__main__":
    threading.Thread(target=consumer, daemon=True).start()

    start = time.perf_counter()
    place_order({"id": 1, "customer": "budi@mail.com",
                 "total": 900_000})
    print("Response: 201 Created")
    ms = (time.perf_counter() - start) * 1000
    print(f"Waktu response: {ms:.0f} ms")

    events.join()            # khusus demo: tunggu consumer selesai
