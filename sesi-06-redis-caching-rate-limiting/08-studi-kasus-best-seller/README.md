# Studi Kasus Hari 3: Produk Terlaris

Dikerjakan **mandiri** setelah Sesi 5 dan Sesi 6. Gunakan materi sesi-sesi sebelumnya: repository, Unit of Work, cache-aside, cache key, invalidation, dan rate limiting.

Mulai dari `before/` (sama dengan hasil hands-on Sesi 6). Kunci jawaban ada di `after/`.

## Latar Belakang

Tim marketing ingin menampilkan **produk terlaris** di halaman depan aplikasi. Halaman depan dibuka oleh semua pengunjung, sedangkan menghitung produk terlaris butuh query yang berat (menjumlahkan item dari semua order). Hasilnya juga tidak harus berubah setiap detik, jadi cocok untuk di-cache.

## Requirement

- Endpoint baru `GET /products/best-sellers?limit=5`.
  - Berisi `product_id`, `name`, dan `sold` (jumlah terjual), diurutkan dari yang paling banyak terjual.
  - Yang dihitung hanya order yang **sudah dibayar** (`paid`). Order `pending` dan `cancelled` tidak dihitung.
  - `limit` minimal 1, maksimal 10, default 5. Di luar itu = 422.
- Hasilnya memakai **cache-aside** di Redis:
  - Cukup **satu cache key**: `v1:products:best-sellers`, berisi top 10. Response dipotong sesuai `limit`.
  - Response punya header `X-Cache`: `MISS` saat dihitung dari database, `HIT` saat diambil dari cache.
- Cache dihapus **setelah commit** setiap ada order yang dibayar, supaya angka terjual langsung terbaru.
- Order baru (masih `pending`) tidak menghapus cache.
- Endpoint ini dibatasi **rate limit** yang sama dengan endpoint order (lewat batas = 429 `rate_limited`).
- `domain/` dan `application/` tetap tanpa `fastapi`, `sqlalchemy`, dan `redis`.

## Langkah Singkat

1. Tambahkan `BEST_SELLERS_KEY` di `application/cache_keys.py`.
2. Tambahkan `best_sellers(limit)` di port `OrderRepository` (`application/ports.py`).
3. Implementasikan query-nya di `SqlAlchemyOrderRepository`: join `order_lines` dengan `orders`, filter status `paid`, `group by` produk, urutkan dari jumlah terbanyak.
4. Repository order mencatat jika ada status order yang berubah (`status_changed`), lalu Unit of Work menghapus `BEST_SELLERS_KEY` setelah commit.
5. Tambahkan `ProductService.best_sellers(limit)` dengan cache-aside. Kembalikan juga informasi cache hit atau miss.
6. Tambahkan schema `BestSellerOut` dan route `GET /products/best-sellers` dengan `Depends(rate_limit)`. Tulis route ini **sebelum** `GET /products/{product_id}`.
7. Tulis test: hanya order dibayar yang dihitung, cache hit tidak query database, order dibayar menghapus cache, validasi `limit`, dan rate limit.

## Contoh Hasil

Setelah order Keyboard 2 dan Mouse 1 dibayar:

```
GET /products/best-sellers?limit=5
X-Cache: MISS

[
  {"product_id": 1, "name": "Keyboard", "sold": 2},
  {"product_id": 2, "name": "Mouse", "sold": 1}
]
```

Request kedua mendapat data yang sama dengan header `X-Cache: HIT`. Setelah ada order lain yang dibayar, request berikutnya kembali `MISS` dengan angka terbaru.

## Kriteria Selesai

- [ ] `GET /products/best-sellers` hanya menghitung order `paid`, urut dari yang terbanyak
- [ ] `limit` di luar 1-10 ditolak 422
- [ ] Request kedua `X-Cache: HIT`, dan database tidak di-query lagi
- [ ] Order dibayar = cache dihapus setelah commit, order `pending` tidak menghapus cache
- [ ] Lewat batas request = 429 dengan format `{"error": {...}}`
- [ ] `pytest` hijau, termasuk test baru untuk produk terlaris

## Menjalankan

```bash
cd sesi-06-redis-caching-rate-limiting
docker compose up -d                 # Redis
cd 08-studi-kasus-best-seller/before # atau after/ untuk kunci jawaban
uvicorn app.main:app --reload
pytest -v
```

## Catatan

- `pytest` tidak butuh Redis, karena test memakai `fakeredis` (lihat `tests/conftest.py`).
- Query produk terlaris ikut disimulasikan lambat lewat `QUERY_DELAY`, sama seperti query produk.
- Worker Celery tidak wajib untuk studi kasus ini. Tanpa worker, notifikasi order hanya menumpuk di queue Redis.
