"""Async IO - BEFORE

Endpoint memakai `async def`, tapi di dalamnya ada time.sleep (blocking).
Selama time.sleep berjalan, event loop berhenti dan request lain ikut menunggu.
3 request bersamaan = 3 x 1 detik = sekitar 3 detik.

Jalankan demo: python before.py
Atau server:   uvicorn before:app --reload
"""
import asyncio
import time

import httpx
from fastapi import FastAPI

app = FastAPI()


def fetch_shipping_cost(city: str) -> int:
    time.sleep(1)                     # anggap: memanggil API ekspedisi, butuh 1 detik
    return 20_000


@app.get("/shipping/{city}")
async def shipping_cost(city: str):
    return {"city": city, "cost": fetch_shipping_cost(city)}   # blocking di dalam async


async def demo():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        start = time.perf_counter()
        await asyncio.gather(*(client.get(f"/shipping/{city}") for city in ["jakarta", "bandung", "surabaya"]))
        print(f"3 request selesai dalam {time.perf_counter() - start:.1f} detik")   # ~3.0


if __name__ == "__main__":
    asyncio.run(demo())
