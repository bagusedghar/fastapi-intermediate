# Order API

API untuk toko online: produk, order dengan diskon per tipe customer,
pembayaran, report penjualan, dan notifikasi ke customer.

## Arsitektur

Lihat [docs/architecture.md](docs/architecture.md) untuk diagram dan alur
request. Keputusan teknis penting dicatat di [docs/adr/](docs/adr/).

## Menjalankan

Butuh Docker. Semua service (API, worker, consumer, PostgreSQL, Redis,
RabbitMQ) berjalan di container.

```bash
cp .env.example .env                 # isi JWT_SECRET, minimal 32 karakter
docker compose up -d --build
docker compose exec api python create_user.py admin@toko.com --role admin
```

| URL | Isi |
|---|---|
| http://localhost:8000/docs | Dokumentasi API (Swagger), hanya saat `ENV=development` |
| http://localhost:8000/health/ready | Readiness check |
| http://localhost:16686 | Trace di Jaeger |

## Konfigurasi

| Variabel | Wajib | Default | Keterangan |
|---|---|---|---|
| `JWT_SECRET` | ya | - | Kunci tanda tangan JWT, minimal 32 karakter |
| `DATABASE_URL` | tidak | PostgreSQL lokal | Koneksi database |
| `ENV` | tidak | `development` | `production` mematikan `/docs` |

## Test

```bash
pip install -r requirements-dev.txt
ruff check .
pytest -q                            # tanpa Docker: SQLite + fakeredis
BASE_URL=http://localhost:8000 python smoke_test.py
```

## Deploy

Setiap pull request menjalankan lint, test, build, dan scan image. Setelah
merge ke `main`, image di-push ke `ghcr.io` dan di-deploy ke Kubernetes
(`k8s/`), lalu smoke test dijalankan.
