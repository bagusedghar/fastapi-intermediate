"""Background Job - AFTER (FastAPI BackgroundTasks)

Email dijadwalkan untuk dikirim SETELAH response terkirim.
Client langsung dapat data order, email menyusul beberapa detik kemudian.

BackgroundTasks cocok untuk pekerjaan ringan yang boleh hilang kalau server restart.
Untuk pekerjaan yang lama, berat, atau harus bisa di-retry, pakai worker terpisah (Celery).

Jalankan: uvicorn after:app --reload
Coba POST /orders di /docs: response langsung keluar, log [EMAIL] muncul 3 detik kemudian.
"""
import time

from fastapi import BackgroundTasks, FastAPI

app = FastAPI()
ORDERS: dict[int, dict] = {}


def send_email(to: str, message: str) -> None:
    time.sleep(3)
    print(f"[EMAIL] ke {to}: {message}")


@app.post("/orders", status_code=201)
def create_order(customer: str, total: int,
                 background_tasks: BackgroundTasks):
    order_id = len(ORDERS) + 1
    order = {"id": order_id, "customer": customer, "total": total}
    ORDERS[order_id] = order
    background_tasks.add_task(
        send_email, customer, f"Order #{order_id} berhasil"
    )
    return order                  # langsung dikirim ke client
