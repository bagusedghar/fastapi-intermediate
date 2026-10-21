"""Idempotency - AFTER

Task idempotent: dijalankan sekali atau berkali-kali, hasil akhirnya sama.
Caranya dengan idempotency key, yaitu penanda unik untuk satu pekerjaan.
Sebelum mengirim email, task mengecek apakah key itu sudah pernah diproses.

Di aplikasi nyata SENT_KEYS disimpan di database (kolom unique) atau Redis (SET ... NX),
supaya semua worker melihat data yang sama.

Jalankan demo: python after.py
"""
from celery import Celery

celery_app = Celery("demo", broker="redis://localhost:6379/0", backend="redis://localhost:6379/1")

INBOX: list[str] = []
SENT_KEYS: set[str] = set()           # anggap: tabel sent_emails
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
    key = f"payment-email:{order_id}"   # idempotency key
    if key in SENT_KEYS:
        print(f"[SKIP] {key} sudah terkirim")
    else:
        send_email(to, f"Order #{order_id} sudah dibayar")
        SENT_KEYS.add(key)            # tandai langsung setelah email terkirim
    save_email_log(order_id)


if __name__ == "__main__":
    celery_app.conf.task_always_eager = True
    send_payment_email.delay(1, "budi@mail.com")      # retry karena database timeout
    send_payment_email.delay(1, "budi@mail.com")      # job yang sama masuk dua kali
    print("Email yang diterima customer:", len(INBOX))   # 1
