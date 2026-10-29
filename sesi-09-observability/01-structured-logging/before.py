"""Structured Logging - BEFORE (log berupa kalimat bebas)

Setiap developer menulis log dengan kalimatnya sendiri. Data penting (order_id, customer)
diselipkan di tengah kalimat, dengan format yang berbeda-beda.
Saat production error, kita ingin mencari semua log untuk order 2.
Pencarian teks "order #2" hanya menemukan sebagian log.

Jalankan: python before.py
"""
import io
import logging

stream = io.StringIO()                   # tempat log, anggap: file log
logging.basicConfig(
    level=logging.INFO, stream=stream,
    format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("orders")


def place_order(order_id: int, customer: str, total: int):
    logger.info(f"Order #{order_id} dibuat oleh {customer}")
    logger.info(f"Total order_id={order_id}: Rp{total:,}")
    if total > 1_000_000:
        logger.warning(f"Pembayaran Order {order_id} ditolak bank")


if __name__ == "__main__":
    place_order(1, "ani@mail.com", 300_000)
    place_order(2, "budi@mail.com", 1_500_000)

    lines = stream.getvalue().splitlines()
    print("\n".join(lines))
    found = [line for line in lines if "order #2" in line.lower()]
    print(f"\nCari 'order #2': {len(found)} dari 3 log order 2")
