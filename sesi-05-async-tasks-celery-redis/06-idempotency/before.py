"""Idempotency - BEFORE

Task mengirim email, lalu menyimpan log ke database.
Penyimpanan log gagal sekali (database timeout), task di-retry dari awal,
dan email terkirim lagi. Customer menerima email yang sama dua kali.

Hal yang sama terjadi kalau job yang sama masuk antrean dua kali
(misalnya user klik tombol dua kali, atau worker mati sebelum sempat lapor selesai).

Jalankan demo: python before.py
"""
from celery import Celery

celery_app = Celery("demo", broker="redis://localhost:6379/0", backend="redis://localhost:6379/1")

INBOX: list[str] = []                 # anggap: inbox email customer
log_attempts = 0


def send_email(to: str, message: str) -> None:
    INBOX.append(message)
    print(f"[EMAIL] ke {to}: {message}")


def save_email_log(order_id: int) -> None:
    global log_attempts
    log_attempts += 1
    if log_attempts == 1:
        raise ConnectionError("Database timeout")


@celery_app.task(autoretry_for=(ConnectionError,), max_retries=3)
def send_payment_email(order_id: int, to: str) -> None:
    send_email(to, f"Order #{order_id} sudah dibayar")
    save_email_log(order_id)          # gagal sekali -> retry -> email dikirim lagi


if __name__ == "__main__":
    celery_app.conf.task_always_eager = True
    send_payment_email.delay(1, "budi@mail.com")
    print("Email yang diterima customer:", len(INBOX))   # 2
