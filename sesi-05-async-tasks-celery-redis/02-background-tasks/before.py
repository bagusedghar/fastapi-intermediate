"""Background Job - BEFORE

Email konfirmasi dikirim di dalam request.
Client harus menunggu email terkirim (3 detik) padahal yang dia butuhkan cuma data order.
Kalau server email lambat atau mati, membuat order ikut lambat atau gagal.

Jalankan: uvicorn before:app --reload
Coba POST /orders di /docs, perhatikan waktu response-nya.
"""
import time

from fastapi import FastAPI

app = FastAPI()
ORDERS: dict[int, dict] = {}


def send_email(to: str, message: str) -> None:
    time.sleep(3)                     # anggap: kirim lewat SMTP, butuh 3 detik
    print(f"[EMAIL] ke {to}: {message}")


@app.post("/orders", status_code=201)
def create_order(customer: str, total: int):
    order = {"id": len(ORDERS) + 1, "customer": customer, "total": total}
    ORDERS[order["id"]] = order
    send_email(customer, f"Order #{order['id']} berhasil")     # client ikut menunggu 3 detik
    return order
