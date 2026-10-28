"""Failure Handling - BEFORE

Server email mati total. Error ditangkap dengan except Exception lalu cuma di-print.
Akibatnya:
- retry tidak pernah jalan, karena Celery tidak melihat ada error
- status task SUCCESS, padahal email tidak terkirim
- tidak ada yang tahu, tidak ada data untuk dijalankan ulang

Jalankan demo: python before.py
"""
from celery import Celery

celery_app = Celery("demo",
                    broker="redis://localhost:6379/0",
                    backend="redis://localhost:6379/1")


class EmailServiceDown(Exception):
    pass


def send_email(to: str, message: str) -> None:
    raise EmailServiceDown("Server email tidak bisa dihubungi")


@celery_app.task(autoretry_for=(EmailServiceDown,), max_retries=3)
def send_order_email(to: str, message: str) -> None:
    try:
        send_email(to, message)
    except Exception as e:
        print("error:", e)        # error hanya di-print


if __name__ == "__main__":
    celery_app.conf.task_always_eager = True
    result = send_order_email.delay("budi@mail.com",
                                    "Order #1 berhasil")
    print("Status:", result.state)    # SUCCESS, padahal gagal
