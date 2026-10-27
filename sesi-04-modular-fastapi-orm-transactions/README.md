# Sesi 4 - Advanced FastAPI Architecture & ORM Transactions

**Chapter:** Scalable FastAPI Applications

## Learning Outcome

- Mendesain FastAPI modular dengan routing, dependency injection, service, dan data access terpisah.
- Mengelola sesi ORM dan transaksi yang atomic, termasuk rollback ketika terjadi error.
- Menerapkan penanganan error API yang konsisten dan dokumentasi OpenAPI yang terstruktur.

## Isi Folder

Setiap topik punya dua file: `before.py` (masalahnya) dan `after.py` (setelah konsepnya diterapkan).

| Folder | Topik | Yang dibahas |
|---|---|---|
| [`01-apirouter`](01-apirouter) | APIRouter | Semua endpoint di `main.py` dipecah per fitur dengan `APIRouter` |
| [`02-schemas`](02-schemas) | Schemas | Schema request dan response dipisah, `cost_price` tidak bocor ke client |
| [`03-dependency-graph`](03-dependency-graph) | Dependency Graph | `get_session` (yield) → `get_repository` → route, session pasti ditutup |
| [`04-middleware`](04-middleware) | Middleware | Logging dan header `X-Process-Time` untuk semua request, ditulis sekali |
| [`05-exception-handling`](05-exception-handling) | Exception Handling | Satu exception handler, format error seragam |
| [`06-openapi`](06-openapi) | OpenAPI | Judul, versi, tags, summary, response model, dan contoh request di `/docs` |
| [`07-transaction`](07-transaction) | Transaction Boundary | Commit per langkah vs satu transaksi dengan `session.begin()` |
| [`08-unit-of-work`](08-unit-of-work) | Unit of Work | Repository tidak commit sendiri, service yang menentukan lewat `uow.commit()` |
| [`09-modular-api`](09-modular-api) | Hands-on | `before/` (hasil Sesi 3) → `after/` (SQLAlchemy, Unit of Work, produk + stok, error handler, middleware) |
| [`10-studi-kasus-voucher`](10-studi-kasus-voucher) | Studi Kasus | Tugas mandiri hari 2: voucher belanja dengan kuota. Soal di README folder itu |
| `slides/` | | Materi presentasi |

## Persiapan

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Menjalankan Contoh

Folder 07 dan 08 cukup Python biasa:

```bash
cd 07-transaction
python before.py
python after.py
```

Folder 01 sampai 06 memakai FastAPI:

```bash
cd 01-apirouter
uvicorn before:app --reload
uvicorn after:app --reload
```

Buka http://127.0.0.1:8000/docs untuk mencoba endpoint-nya. Contoh yang memakai database (03, 07, 08) memakai SQLite di memory, jadi tidak ada file database yang dibuat.

## Hands-on: API Modular dengan Transaksi Multi-step

Mulai dari `09-modular-api/before/` (hasil akhir Sesi 3). Salin jadi folder kerja baru `latihan/`, lalu kembangkan langkah demi langkah bersama mentor sesuai slide hands-on. Hasil akhirnya seperti `after/`.

```
after/
├── app/
│   ├── domain/            # Money, Order, Product (stok), DiscountPolicy, errors
│   ├── application/       # ports (repository, UnitOfWork), OrderService, ProductService
│   ├── infrastructure/    # database, ORM models, repositories, unit_of_work, config
│   ├── api/
│   │   ├── routers/       # orders.py, products.py
│   │   ├── schemas.py     # request & response
│   │   ├── dependencies.py
│   │   ├── errors.py      # exception handler global
│   │   └── middleware.py
│   └── main.py
└── tests/                 # test use case (fake UoW), test transaksi, test API
```

Kriteria selesai:

- [ ] Endpoint dipecah ke `api/routers/` dan schema ke `api/schemas.py`
- [ ] Repository memakai SQLAlchemy dan tidak commit sendiri
- [ ] Buat order mengurangi stok semua item dalam satu Unit of Work
- [ ] Kalau satu item stoknya kurang, tidak ada stok yang berkurang dan order tidak tersimpan
- [ ] Cancel order mengembalikan stok
- [ ] Semua error memakai format `{"error": {"code", "message", "details"}}`
- [ ] Setiap response punya header `X-Process-Time`
- [ ] `/docs` menampilkan tags, summary, dan response error, `pytest` hijau

Kunci jawaban ada di `after/`:

```bash
cd 09-modular-api/after
uvicorn app.main:app --reload
pytest -v
```

Contoh request:

```bash
curl -X POST localhost:8000/products -H "Content-Type: application/json" \
  -d '{"name": "Keyboard", "price": 500000, "stock": 5}'
curl -X POST localhost:8000/orders -H "Content-Type: application/json" \
  -d '{"customer": "budi@mail.com", "customer_type": "vip", "items": [{"product_id": 1, "qty": 2}]}'
curl -X POST localhost:8000/orders/1/cancel     # stok Keyboard kembali ke 5
```

## Studi Kasus: Voucher Belanja

Tugas mandiri di akhir hari kedua, menggabungkan materi Sesi 3 dan Sesi 4. Soal, requirement, dan contoh hasilnya ada di [`10-studi-kasus-voucher/README.md`](10-studi-kasus-voucher/README.md). Mulai dari `before/`, kunci jawaban di `after/`.

```bash
cd 10-studi-kasus-voucher/after
uvicorn app.main:app --reload
pytest -v
```

## Catatan

- Request order sekarang berisi `product_id` dan `qty`, bukan nama dan harga. Harga diambil dari data produk.
- Database diatur lewat environment variable `DATABASE_URL` (default `sqlite:///orders.db`). Kalau masih ada `orders.db` dari sesi sebelumnya, hapus dulu karena struktur tabelnya berbeda.
- Notifikasi dikirim setelah commit, jadi order yang gagal tidak pernah mengirim email.
