"""Sync vs Async - BEFORE (semua dipanggil langsung)

Setelah order disimpan, place_order memanggil layanan lain satu per satu dan menunggu jawabannya.
- Waktu response = jumlah waktu semua layanan
- Satu layanan mati (analytics), request ikut error, padahal order sudah tersimpan
- Ada layanan baru yang perlu tahu soal order = place_order diubah lagi

Jalankan: python before.py
"""
import time


def reserve_stock(order):
    time.sleep(0.05)      # harus sync: order sah jika stoknya ada


def send_email(order):
    time.sleep(0.8)                       # server email lambat
    print(f"  [email] order #{order['id']} terkirim "
          f"ke {order['customer']}")


def add_points(order):
    time.sleep(0.3)
    points = order["total"] // 10_000
    print(f"  [points] +{points} poin untuk {order['customer']}")


def update_analytics(order):
    raise ConnectionError("analytics service tidak merespons")


def place_order(order):
    reserve_stock(order)               # harus sync
    print(f"  [order] order #{order['id']} disimpan")
    send_email(order)                  # 0.8 s
    add_points(order)                  # 0.3 s
    update_analytics(order)            # service mati
    return order


if __name__ == "__main__":
    start = time.perf_counter()
    try:
        place_order({"id": 1, "customer": "budi@mail.com",
                     "total": 900_000})
        print("Response: 201 Created")
    except ConnectionError as exc:
        print(f"Response: 500 Internal Server Error ({exc})")
    ms = (time.perf_counter() - start) * 1000
    print(f"Waktu response: {ms:.0f} ms")
