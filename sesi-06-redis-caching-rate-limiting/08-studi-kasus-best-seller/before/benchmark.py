"""Bandingkan latency GET /products/{id}: cache miss vs cache hit.

Jalankan API dulu (lihat app/main.py), lalu dari folder after/: python benchmark.py

Query produk disimulasikan lambat lewat QUERY_DELAY (default 0.2 detik),
supaya perbedaan database vs cache terlihat jelas.
"""
import statistics
import time

import httpx

BASE_URL = "http://127.0.0.1:8000"


def timed_get(client: httpx.Client, url: str) -> tuple[float, httpx.Response]:
    start = time.perf_counter()
    response = client.get(url)
    return (time.perf_counter() - start) * 1000, response


with httpx.Client(base_url=BASE_URL) as client:
    product = client.post("/products", json={"name": "Monitor", "price": 2_000_000, "stock": 50}).json()
    url = f"/products/{product['id']}"

    miss, _ = timed_get(client, url)                              # cache kosong -> database
    hits = [timed_get(client, url)[0] for _ in range(20)]         # dari cache

    client.post("/orders", json={"customer": "budi@mail.com",
                                 "items": [{"product_id": product["id"], "qty": 1}]})
    after_order, response = timed_get(client, url)                # cache dihapus -> database lagi

print(f"Request pertama (MISS)          : {miss:7.1f} ms")
print(f"20 request berikutnya (HIT)     : {statistics.median(hits):7.1f} ms (median)")
print(f"Setelah order, stok berubah     : {after_order:7.1f} ms, stok = {response.json()['stock']}")
