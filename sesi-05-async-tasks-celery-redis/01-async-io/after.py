"""Async IO - AFTER

Selama menunggu IO (API lain, database, file), event loop melayani request lain.
Syaratnya: yang ditunggu memakai library async dan dipanggil dengan `await`.
3 request bersamaan = sekitar 1 detik.

Kalau library-nya tidak async (misalnya requests), pakai `def` biasa.
FastAPI akan menjalankannya di thread pool supaya event loop tidak berhenti.

Async IO cocok untuk pekerjaan singkat yang hasilnya dibutuhkan di response.
Pekerjaan lama (report, kirim email massal) tetap membuat client menunggu: itu tugas background job.

Jalankan demo: python after.py
Atau server:   uvicorn after:app --reload
"""
import asyncio
import time

import httpx
from fastapi import FastAPI

app = FastAPI()


async def fetch_shipping_cost(city: str) -> int:
    await asyncio.sleep(1)            # di aplikasi nyata: await client.get("https://api-ekspedisi/...")
    return 20_000


@app.get("/shipping/{city}")
async def shipping_cost(city: str):
    return {"city": city, "cost": await fetch_shipping_cost(city)}


async def demo():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        start = time.perf_counter()
        await asyncio.gather(*(client.get(f"/shipping/{city}") for city in ["jakarta", "bandung", "surabaya"]))
        print(f"3 request selesai dalam {time.perf_counter() - start:.1f} detik")   # ~1.0


if __name__ == "__main__":
    asyncio.run(demo())
