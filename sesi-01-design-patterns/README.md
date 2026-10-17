# Sesi 1 - Python Design Patterns for Backend

**Chapter:** Software Architecture & Design Patterns

## Learning Outcome

- Membandingkan Factory, Singleton, Strategy, dan Repository beserta trade-off-nya.
- Memisahkan persistence logic dari business logic melalui Repository dan Service Layer.
- Me-refactor modul FastAPI agar mudah diuji, diperluas, dan di-maintain.

## Isi Folder

Setiap pattern punya dua file: `before.py` (masalahnya) dan `after.py` (setelah pattern dipakai).

| Folder | Topik | Yang dibahas |
|---|---|---|
| [`01-factory`](01-factory) | Factory | If/elif pembuatan notifier diganti `create_notifier()` |
| [`02-singleton`](02-singleton) | Singleton | Config dibaca sekali lewat `@lru_cache` |
| [`03-strategy`](03-strategy) | Strategy | Aturan diskon per tipe customer jadi class terpisah |
| [`04-repository`](04-repository) | Repository | SQL dipisah dari perhitungan, ada versi SQLite dan in-memory |
| [`05-service-layer`](05-service-layer) | Service Layer | Business logic keluar dari endpoint FastAPI |
| [`06-refactor-order-api`](06-refactor-order-api) | Hands-on | API sederhana: `before/` (satu file) → `after/` (semua pattern) |
| `slides/` | | Materi presentasi |

## Persiapan

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Menjalankan Contoh

Folder 01 sampai 04 cukup Python biasa:

```bash
cd 01-factory
python before.py
python after.py
```

Folder 05 memakai FastAPI:

```bash
cd 05-service-layer
uvicorn before:app --reload
uvicorn after:app --reload
```

## Hands-on: Refactor Order API

Mulai dari `06-refactor-order-api/before/main.py`, lalu pecah ke beberapa file seperti di `after/`.

```bash
cd 06-refactor-order-api/before
uvicorn main:app --reload        # buka http://127.0.0.1:8000/docs
```

Contoh request:

```bash
curl -X POST localhost:8000/orders -H "Content-Type: application/json" \
  -d '{"customer": "budi@mail.com", "customer_type": "vip", "items": [{"name": "Keyboard", "price": 500000, "qty": 2}]}'
```

Kriteria selesai:

- [ ] `POST /orders` dan `GET /orders/{id}` tetap jalan dengan response yang sama
- [ ] `service.py` tidak import `fastapi` maupun `sqlite3`
- [ ] Tipe customer baru bisa ditambah tanpa mengubah `service.py`
- [ ] Unit test service jalan tanpa database
- [ ] `pytest` hijau

Kunci jawaban ada di `after/`:

```bash
cd 06-refactor-order-api/after
uvicorn main:app --reload
pytest -v
```

Channel notifikasi bisa diganti lewat environment variable `NOTIFICATION_CHANNEL=sms`.

## Catatan

- Contoh sengaja dibuat sederhana dan memakai `sqlite3` bawaan Python supaya fokus ke pattern, bukan ke ORM.
- `get_order_service()` di `after/main.py` adalah titik masuk ke materi Dependency Injection di Sesi 2.
