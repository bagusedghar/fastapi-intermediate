"""Correlation ID - AFTER (setiap request punya request_id)

Middleware memberi setiap request sebuah request_id:
- Diambil dari header X-Request-ID jika client atau gateway sudah mengirimnya
- Dibuat baru jika belum ada
request_id disimpan di contextvars (nilai yang terpisah per request, aman untuk async),
lalu logging.Filter menempelkannya ke SETIAP log. Response juga membawa header X-Request-ID,
jadi customer atau tim support punya nomor yang bisa dicari di log.

Jalankan: python after.py
"""
import asyncio
import logging
import uuid
from contextvars import ContextVar

import httpx
from fastapi import FastAPI, Request

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()   # tempel ke log
        return True


handler = logging.StreamHandler()
handler.addFilter(RequestIdFilter())
logging.basicConfig(
    level=logging.INFO, handlers=[handler],
    format="%(levelname)-7s [%(request_id)s] %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)   # log client demo
logger = logging.getLogger("orders")
app = FastAPI()


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = (request.headers.get("X-Request-ID")
                  or uuid.uuid4().hex[:8])
    request_id_var.set(request_id)       # berlaku di request ini saja
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.post("/orders")
async def create_order(customer: str):
    logger.info("simpan order")
    await asyncio.sleep(0.1)         # anggap: menyimpan ke database
    logger.info("kirim event order.placed")
    if customer == "budi@mail.com":
        logger.error("event gagal dikirim")
    return {"status": "created"}


async def main():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport,
                                 base_url="http://api") as client:
        customers = ["ani@mail.com", "budi@mail.com", "siti@mail.com"]
        responses = await asyncio.gather(*(
            client.post("/orders", params={"customer": c})
            for c in customers))
    for customer, response in zip(customers, responses):
        print(f"{customer}: {response.status_code}, "
              f"header X-Request-ID = "
              f"{response.headers.get('X-Request-ID')}")


if __name__ == "__main__":
    asyncio.run(main())
