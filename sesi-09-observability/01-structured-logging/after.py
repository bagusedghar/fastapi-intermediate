"""Structured Logging - AFTER (satu log = satu baris JSON)

JsonFormatter mengubah setiap log menjadi satu baris JSON.
Data penting dikirim lewat extra={...}, jadi menjadi field sendiri, bukan bagian dari kalimat.
Mencari log order 2 cukup dengan filter field order_id == 2.
Di production, tool seperti Grafana Loki atau Elasticsearch membaca field ini.

Jalankan: python after.py
"""
import io
import json
import logging
from datetime import datetime, timezone

# atribut bawaan setiap LogRecord, selain ini berarti dari extra={...}
STANDARD = set(vars(logging.makeLogRecord({}))) | {"message"}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        time = datetime.fromtimestamp(record.created, timezone.utc)
        log = {
            "time": time.isoformat(timespec="seconds"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key, value in vars(record).items():
            if key not in STANDARD:
                log[key] = value                 # field dari extra
        return json.dumps(log)


stream = io.StringIO()                   # tempat log, anggap: file log
handler = logging.StreamHandler(stream)
handler.setFormatter(JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger("orders")


def place_order(order_id: int, customer: str, total: int):
    fields = {"order_id": order_id, "customer": customer}
    logger.info("order dibuat", extra=fields)
    logger.info("total dihitung", extra={**fields, "total": total})
    if total > 1_000_000:
        logger.warning("pembayaran ditolak", extra=fields)


if __name__ == "__main__":
    place_order(1, "ani@mail.com", 300_000)
    place_order(2, "budi@mail.com", 1_500_000)

    lines = stream.getvalue().splitlines()
    print("\n".join(lines))
    found = [line for line in lines
             if json.loads(line)["order_id"] == 2]
    print(f"\nFilter order_id == 2: {len(found)} dari 3 log order 2")
