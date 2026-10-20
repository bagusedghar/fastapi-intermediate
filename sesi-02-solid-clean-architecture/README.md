# Sesi 2 - SOLID, Clean Architecture & Dependency Injection

**Chapter:** Software Architecture & Design Patterns

## Learning Outcome

- Mengidentifikasi pelanggaran SOLID pada codebase dan memperbaiki coupling antar modul.
- Merancang batas dependency antar layer sesuai pendekatan Clean Architecture.
- Menerapkan dependency injection FastAPI dan membuat unit test yang tidak bergantung langsung pada database.

## Isi Folder

Setiap topik punya dua file: `before.py` (masalahnya) dan `after.py` (setelah prinsipnya diterapkan).

| Folder | Topik | Yang dibahas |
|---|---|---|
| [`01-srp`](01-srp) | Single Responsibility | `OrderManager` serba bisa dipecah jadi class dengan satu tugas |
| [`02-ocp`](02-ocp) | Open/Closed | Ongkir per kurir: if/elif diganti class + registry |
| [`03-lsp`](03-lsp) | Liskov Substitution | Subclass diskon yang hasilnya beda arti, plus test kontrak |
| [`04-isp`](04-isp) | Interface Segregation | Interface repository gemuk dipecah jadi `OrderReader` / `OrderWriter` |
| [`05-dip`](05-dip) | Dependency Inversion | Repository dan notifier dikirim lewat constructor |
| [`06-dependency-injection`](06-dependency-injection) | DI di FastAPI | `Depends` + `dependency_overrides` di test |
| [`07-clean-architecture`](07-clean-architecture) | Hands-on | `before/` (hasil Sesi 1) → `after/` (domain, application, infrastructure, api) |
| `slides/` | | Materi presentasi |

## Persiapan

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Menjalankan Contoh

Folder 01 sampai 05 cukup Python biasa:

```bash
cd 01-srp
python before.py
python after.py
```

Folder 06 memakai FastAPI:

```bash
cd 06-dependency-injection
uvicorn before:app --reload
uvicorn after:app --reload
pytest -v                       # test API tanpa menyentuh orders.db
```

## Hands-on: Redesign Struktur Project

Mulai dari `07-clean-architecture/before/` (hasil akhir Sesi 1), lalu susun ulang per layer seperti di `after/`.

```
after/
├── app/
│   ├── domain/          # Order, aturan diskon
│   ├── application/     # ports (interface) + OrderService
│   ├── infrastructure/  # SQLite repository, notifier, config
│   ├── api/             # routes + dependencies (Depends)
│   └── main.py
└── tests/               # fake repository, unit test, test API
```

Kriteria selesai:

- [ ] `POST /orders` dan `GET /orders/{id}` tetap jalan
- [ ] Kode dipecah ke `domain`, `application`, `infrastructure`, `api`
- [ ] `domain/` dan `application/` tidak import `fastapi` maupun `sqlite3`
- [ ] Dependency dirakit lewat `Depends` di `api/dependencies.py`
- [ ] Unit test dan test API pakai fake repository, `pytest` hijau

Kunci jawaban ada di `after/`:

```bash
cd 07-clean-architecture/after
uvicorn app.main:app --reload
pytest -v
```

## Catatan

- Domain sengaja masih sederhana (`Order` berupa dataclass). Entity, value object, dan aggregate dibahas di Sesi 3.
- Repository masih `sqlite3` bawaan Python. Pindah ke SQLAlchemy + transaksi dibahas di Sesi 4.
