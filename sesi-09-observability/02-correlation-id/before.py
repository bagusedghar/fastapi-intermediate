"""Correlation ID - BEFORE (log dari banyak request bercampur)

Server memproses beberapa request bersamaan, jadi log dari request yang berbeda saling bercampur.
Ada log "event gagal dikirim", tetapi tidak ada yang menunjukkan log itu milik request yang mana.
Customer yang komplain juga tidak punya nomor apa pun untuk dicari di log.

Jalankan: python before.py
"""
import asyncio
import logging

import httpx
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO,
                    format="%(levelname)-7s %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)   # log client demo
logger = logging.getLogger("orders")
app = FastAPI()


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
