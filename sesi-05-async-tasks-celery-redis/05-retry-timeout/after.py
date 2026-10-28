"""Retry & Timeout - AFTER

- autoretry_for   : error apa saja yang boleh dicoba lagi (gangguan sementara, bukan bug)
- retry_backoff   : jeda retry makin lama (maksimal 1s, 2s, 4s, ...), supaya server email tidak dibanjiri.
                    Jedanya diacak (jitter) supaya worker tidak retry di detik yang sama
- max_retries     : batas percobaan, setelah itu task dianggap gagal
- soft_time_limit : setelah 10 detik, task diberi SoftTimeLimitExceeded (masih sempat bersih-bersih)
- time_limit      : setelah 15 detik, task dihentikan paksa oleh worker

Jalankan demo: python after.py
(demo memakai mode eager: retry langsung dijalankan tanpa jeda, time limit hanya berlaku di worker)
"""
from celery import Celery

celery_app = Celery("demo",
                    broker="redis://localhost:6379/0",
                    backend="redis://localhost:6379/1")


class EmailServiceDown(Exception):
    pass


attempts = 0


def send_email(to: str, message: str) -> None:
    global attempts
    attempts += 1
    if attempts < 3:
        print(f"  percobaan {attempts}: gagal, server email timeout")
        raise EmailServiceDown("Server email timeout")
    print(f"  percobaan {attempts}: [EMAIL] ke {to}: {message}")


@celery_app.task(autoretry_for=(EmailServiceDown,),
                 retry_backoff=True, max_retries=3,
                 soft_time_limit=10, time_limit=15)
def send_order_email(to: str, message: str) -> None:
    send_email(to, message)


if __name__ == "__main__":
    celery_app.conf.task_always_eager = True
    result = send_order_email.delay("budi@mail.com",
                                    "Order #1 berhasil")
    print("Status:", result.state)    # SUCCESS di percobaan ke-3
