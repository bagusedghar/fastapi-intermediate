# Sesi 6 - Redis Caching, Rate Limiting & API Gateway

**Chapter:** Scalable FastAPI Applications

## Learning Outcome

- Memilih caching strategy dan mendesain cache key, TTL, dan invalidation untuk endpoint FastAPI.
- Menerapkan rate limiting sederhana dan menjelaskan peran API gateway dalam kontrol traffic.
- Mengevaluasi trade-off antara response latency, consistency, dan penggunaan resource.

## Isi Folder

Setiap topik punya dua file: `before.py` (masalahnya) dan `after.py` (setelah konsepnya diterapkan).

| Folder | Topik | Yang dibahas |
|---|---|---|
| [`01-cache-aside`](01-cache-aside) | Cache-Aside | Selalu query database vs cek cache dulu, isi cache saat miss |
| [`02-ttl-invalidation`](02-ttl-invalidation) | TTL & Invalidation | Cache tanpa TTL jadi basi vs TTL + hapus key saat data berubah |
| [`03-response-cache-key`](03-response-cache-key) | Response Cache & Cache Key | Satu key untuk semua query vs key berisi namespace, versi, dan parameter |
| [`04-cache-stampede`](04-cache-stampede) | Cache Stampede | 20 request bersamaan = 20 query vs lock + TTL jitter = 1 query |
| [`05-rate-limiting`](05-rate-limiting) | Rate Limiting | Tanpa batas vs fixed window (`INCR` + `EXPIRE`), 429 + `Retry-After` |
| [`06-sliding-window`](06-sliding-window) | Sliding Window | Celah fixed window di pergantian menit vs sliding window log (sorted set) |
| [`07-cache-rate-limit`](07-cache-rate-limit) | Hands-on | `before/` (hasil Sesi 5) → `after/` (cache produk, rate limit, benchmark latency) |
| [`08-studi-kasus-best-seller`](08-studi-kasus-best-seller) | Studi Kasus | Tugas mandiri hari 3: produk terlaris dengan cache dan rate limit. Soal di README folder itu |
| `docker-compose.yml` | | Redis untuk cache, rate limiter, dan broker Celery |
| `slides/` | | Materi presentasi |

## Persiapan

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
docker compose up -d             # menjalankan Redis di localhost:6379
```

## Menjalankan Contoh

Semua contoh butuh Redis, lalu cukup dijalankan dengan Python:

```bash
cd 01-cache-aside
python before.py
python after.py
```

Contoh 03 dan 05 juga bisa dijalankan sebagai server:

```bash
cd 03-response-cache-key
uvicorn before:app --reload
uvicorn after:app --reload
```

## Hands-on: Redis Cache, Rate Limiter & Perbandingan Latency

Mulai dari `07-cache-rate-limit/before/` (hasil akhir Sesi 5). Salin jadi folder kerja baru `latihan/`, lalu kembangkan langkah demi langkah bersama mentor sesuai slide hands-on. Hasil akhirnya seperti `after/`.

```
after/
├── app/
│   ├── application/
│   │   ├── ports.py            # + port Cache
│   │   ├── cache_keys.py       # nama cache key di satu tempat
│   │   └── product_service.py  # cache-aside untuk detail & daftar produk
│   ├── infrastructure/
│   │   ├── redis_client.py
│   │   ├── cache.py            # RedisCache: JSON + TTL + jitter
│   │   ├── rate_limiter.py     # sliding window dengan sorted set
│   │   ├── repositories.py     # catat produk yang berubah
│   │   └── unit_of_work.py     # hapus cache setelah commit
│   └── api/
│       ├── rate_limit.py       # dependency rate limit + header X-RateLimit-*
│       └── errors.py           # + 429 rate_limited
├── benchmark.py                # bandingkan latency cache miss vs hit
└── tests/                      # + test_cache.py, test_rate_limit.py
```

Kriteria selesai:

- [ ] `GET /products` dan `GET /products/{id}` memakai cache-aside dengan TTL
- [ ] Cache key punya namespace dan versi, diatur di satu tempat
- [ ] Buat order dan cancel order menghapus cache produk yang stoknya berubah, setelah commit
- [ ] Order yang gagal (rollback) tidak menghapus cache
- [ ] Endpoint orders dan reports dibatasi rate limit per client, lewat batas = 429 dengan `Retry-After`
- [ ] Response punya header `X-RateLimit-Limit` dan `X-RateLimit-Remaining`
- [ ] `benchmark.py` menunjukkan perbedaan latency cache miss vs hit, `pytest` hijau

Kunci jawaban ada di `after/`. Jalankan masing-masing di terminal sendiri:

```bash
cd 07-cache-rate-limit/after
celery -A app.worker.celery_app worker --loglevel=info --pool=solo
uvicorn app.main:app --reload
python benchmark.py
pytest -v
```

Contoh hasil `benchmark.py`:

```
Request pertama (MISS)          :   204.7 ms
20 request berikutnya (HIT)     :     1.4 ms (median)
Setelah order, stok berubah     :   203.2 ms, stok = 49
```

## Catatan

- Query produk disimulasikan lambat lewat `QUERY_DELAY` (default 0.2 detik), supaya beda database dan cache terlihat jelas. Set `QUERY_DELAY=0` untuk mematikannya.
- Cache memakai Redis database 2 (`REDIS_URL`, default `redis://localhost:6379/2`), terpisah dari Celery (database 0 dan 1).
- Pengaturan lain lewat environment variable: `CACHE_TTL` (default 60 detik), `RATE_LIMIT` (default 20 request), `RATE_LIMIT_WINDOW` (default 60 detik).
- `pytest` tidak butuh Redis. Test memakai `fakeredis`, yaitu Redis palsu di memory (lihat `tests/conftest.py`).
- Worker Celery tetap diperlukan supaya notifikasi order terkirim, tapi `benchmark.py` tetap jalan tanpa worker.
