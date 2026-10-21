"""Retry & Timeout - BEFORE

Server email sedang gangguan: 2 percobaan pertama gagal, percobaan ke-3 berhasil.
Task tidak punya retry, jadi langsung FAILURE di percobaan pertama dan email tidak pernah terkirim.
Task juga tidak punya batas waktu: kalau server email hang, worker ikut tertahan selamanya.

Jalankan demo: python before.py
(demo memakai mode eager: task langsung dijalankan tanpa Redis dan worker)
"""
from celery import Celery

celery_app = Celery("demo", broker="redis://localhost:6379/0", backend="redis://localhost:6379/1")


class EmailServiceDown(Exception):
    pass


attempts = 0


def send_email(to: str, message: str) -> None:
    global attempts
    attempts += 1
    if attempts < 3:                  # 2 percobaan pertama gagal
        print(f"  percobaan {attempts}: gagal, server email timeout")
        raise EmailServiceDown("Server email timeout")
    print(f"  percobaan {attempts}: [EMAIL] ke {to}: {message}")


@celery_app.task
def send_order_email(to: str, message: str) -> None:
    send_email(to, message)


if __name__ == "__main__":
    celery_app.conf.task_always_eager = True
    result = send_order_email.delay("budi@mail.com", "Order #1 berhasil")
    print("Status:", result.state)    # FAILURE, email tidak pernah terkirim
