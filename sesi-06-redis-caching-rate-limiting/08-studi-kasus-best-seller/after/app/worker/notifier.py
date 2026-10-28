"""Worker: adapter port Notifier yang mengirim lewat queue Celery.

OrderService tidak berubah sama sekali. Dulu notifier mengirim langsung,
sekarang cuma menaruh job ke queue, jadi response API tidak menunggu server email.
"""
import hashlib

from app.worker.tasks import send_notification


class QueuedNotifier:
    def send(self, to: str, message: str) -> None:
        key = hashlib.sha256(f"{to}|{message}".encode()).hexdigest()   # notifikasi sama = key sama
        send_notification.delay(key, to, message)
