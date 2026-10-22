# Sesi 7 - Database Optimization, Replication & Sharding

**Chapter:** Data & System Reliability

## Learning Outcome

- Menggunakan execution plan untuk mengidentifikasi slow query, N+1, dan kebutuhan indexing.
- Melakukan query optimization dan membandingkan metrik performa sebelum dan sesudah perbaikan.
- Menjelaskan kapan replication atau sharding relevan, termasuk risiko consistency dan operational complexity.

## Isi Folder

Setiap topik punya dua file: `before.py` (masalahnya) dan `after.py` (setelah konsepnya diterapkan).

| Folder | Topik | Yang dibahas |
|---|---|---|
| [`01-explain-analyze`](01-explain-analyze) | EXPLAIN ANALYZE | Cuma tahu waktunya vs membaca execution plan (Seq Scan, Rows Removed by Filter) |
| [`02-index`](02-index) | Index | Seq Scan di 200.000 order vs Index Scan dengan index `(customer, created_at DESC)` |
| [`03-n-plus-one`](03-n-plus-one) | N+1 Query | 100 order = 101 query (lazy load) vs `selectinload` = 2 query |
| [`04-pagination`](04-pagination) | Pagination | `OFFSET` makin lambat di halaman jauh vs keyset pagination (`WHERE id < :after`) |
| [`05-connection-pool`](05-connection-pool) | Connection Pool | Koneksi baru setiap request (`NullPool`) vs koneksi dipakai ulang (`pool_size`) |
| [`06-query-tuning`](06-query-tuning) | Query Tuning | Hitung di Python (600.000 baris) vs `GROUP BY` di database (3 baris) |
| [`07-query-optimization`](07-query-optimization) | Hands-on | `before/` (hasil Sesi 6) → `after/` (PostgreSQL, index, tanpa N+1, keyset pagination, report di SQL) |
| `seed_demo.py` | | Mengisi database `demo` untuk contoh 01-06 |
| `docker-compose.yml` | | PostgreSQL (database `orders` dan `demo`) dan Redis |
| `slides/` | | Materi presentasi |

Replication dan sharding dibahas di slide saja, tanpa contoh kode.

## Persiapan

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
docker compose up -d             # PostgreSQL di localhost:5432, Redis di localhost:6379
python seed_demo.py              # isi database demo, sekali saja
```

## Menjalankan Contoh

Semua contoh butuh PostgreSQL dan data demo, lalu cukup dijalankan dengan Python:

```bash
cd 01-explain-analyze
python before.py
python after.py
```

Contoh hasil (angka di laptop kamu bisa berbeda):

| Contoh | Before | After |
|---|---|---|
| 02 Index | Seq Scan, 9.6 ms | Index Scan, 0.06 ms |
| 03 N+1 | 101 query, 43 ms | 2 query, 9 ms |
| 04 Pagination (halaman 9000) | 24.9 ms | 1.4 ms |
| 05 Connection pool (500 request) | 500 koneksi, 925 ms | 10 koneksi, 527 ms |
| 06 Query tuning | 600.000 baris, 1314 ms | 3 baris, 109 ms |

## Hands-on: Profiling & Optimasi Query PostgreSQL

Mulai dari `07-query-optimization/before/` (hasil akhir Sesi 6), lalu kembangkan seperti di `after/`.
Di `before/` sudah disiapkan `seed.py` (isi 20.000 order) dan `profile_queries.py` (ukur waktu dan jumlah query), supaya bisa diukur sebelum diubah.

```
after/
├── app/
│   ├── application/
│   │   ├── ports.py            # OrderRepository: list_for_customer, sales_summary
│   │   ├── order_service.py    # + list_orders
│   │   └── report_service.py   # report dihitung di database
│   ├── infrastructure/
│   │   ├── config.py           # default PostgreSQL + setting pool
│   │   ├── database.py         # connection pool
│   │   ├── models.py           # index orders (customer, id) dan order_lines (order_id)
│   │   └── repositories.py     # selectinload, keyset pagination, query agregat
│   └── api/
│       ├── schemas.py          # + OrderPageOut
│       └── routers/orders.py   # + GET /orders?customer=&limit=&after=
├── seed.py
├── profile_queries.py
└── tests/                      # + test_query_performance.py
```

Kriteria selesai:

- [ ] Aplikasi memakai PostgreSQL, connection pool diatur lewat config
- [ ] `profile_queries.py` dijalankan di `before/` dan `after/`, hasilnya dibandingkan
- [ ] Report penjualan dihitung di database dengan satu query, bukan memuat semua order
- [ ] Index untuk `order_lines.order_id` dan `orders (customer, id)`, dicek dengan `EXPLAIN ANALYZE`
- [ ] `GET /orders?customer=...` memakai keyset pagination, item di-load dengan `selectinload` (tanpa N+1)
- [ ] `pytest` hijau, termasuk test jumlah query

Kunci jawaban ada di `after/`. Langkah mengukur:

```bash
cd 07-query-optimization/before
python seed.py
python profile_queries.py

cd ../after
python seed.py
python profile_queries.py
```

Contoh hasil `profile_queries.py`:

```
before/
Report penjualan       :  31970.9 ms, 20001 query
Detail order (median)  :      2.3 ms, 2 query

after/
Report penjualan       :     28.4 ms, 1 query
Detail order (median)  :      1.2 ms, 2 query
```

Menjalankan aplikasi `after/`, masing-masing di terminal sendiri:

```bash
cd 07-query-optimization/after
celery -A app.worker.celery_app worker --loglevel=info --pool=solo
uvicorn app.main:app --reload
pytest -v
```

## Catatan

- `seed.py` menghapus semua tabel aplikasi lalu membuatnya ulang dari model. Jalankan ulang setiap pindah antara `before/` dan `after/`, karena index ikut dibuat sesuai model masing-masing.
- `before/` masih memakai SQLite sebagai default saat dijalankan dengan uvicorn. `seed.py` dan `profile_queries.py` selalu memakai PostgreSQL (`DATABASE_URL`, default `postgresql+psycopg://app:app@localhost:5432/orders`).
- Simulasi lambat dari sesi sebelumnya (`QUERY_DELAY`, `REPORT_DELAY`) dihapus di `after/`. Sekarang datanya sungguhan, jadi yang diukur adalah query yang sebenarnya.
- Pengaturan pool lewat environment variable: `DB_POOL_SIZE` (default 5) dan `DB_MAX_OVERFLOW` (default 10), per proses.
- `pytest` tidak butuh PostgreSQL. Test memakai SQLite di memory, dan jumlah query dihitung dengan event SQLAlchemy.
- Contoh 01-06 memakai database `demo`, terpisah dari database aplikasi. Database `demo` dibuat otomatis oleh `postgres-init/` saat container PostgreSQL pertama kali dibuat. Kalau container sudah ada sebelumnya, jalankan `docker compose down -v` lalu `docker compose up -d`.
