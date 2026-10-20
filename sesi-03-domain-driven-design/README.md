# Sesi 3 - Domain-Driven Design (DDD) Fundamentals

**Chapter:** Software Architecture & Design Patterns

## Learning Outcome

- Mengidentifikasi bounded context dan menyusun ubiquitous language dari sebuah use case bisnis.
- Membedakan entity, value object, aggregate, dan domain service beserta tanggung jawabnya.
- Memisahkan domain rules dari FastAPI routes dan persistence implementation.

## Isi Folder

Setiap topik punya dua file: `before.py` (masalahnya) dan `after.py` (setelah konsepnya diterapkan).

| Folder | Topik | Yang dibahas |
|---|---|---|
| [`01-ubiquitous-language`](01-ubiquitous-language) | Ubiquitous Language | `process(data, 2)` diganti nama yang sama dengan istilah bisnis: `pay_order`, `OrderStatus.PAID` |
| [`02-bounded-context`](02-bounded-context) | Bounded Context | Satu `Customer` gemuk dipecah jadi model per context: Sales dan Shipping |
| [`03-value-object`](03-value-object) | Value Object | Harga `int` biasa diganti `Money` yang immutable dan tidak bisa negatif |
| [`04-entity`](04-entity) | Entity | Order punya identitas (id) dan status hanya berubah lewat `pay()` / `cancel()` |
| [`05-aggregate`](05-aggregate) | Aggregate | Item hanya bisa ditambah lewat `Order.add_item()`, total selalu konsisten |
| [`06-domain-service`](06-domain-service) | Domain Service | Aturan diskon dipindah dari `Order` ke `DiscountPolicy` |
| [`07-domain-vs-orm`](07-domain-vs-orm) | Domain Model vs ORM Model | `Order` (domain) dipisah dari `OrderRecord` (SQLAlchemy), repository yang menerjemahkan |
| [`08-ddd-order`](08-ddd-order) | Hands-on | `before/` (hasil Sesi 2) → `after/` (Money, Order aggregate, DiscountPolicy, use case bayar & batal) |
| `slides/` | | Materi presentasi |

## Persiapan

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Menjalankan Contoh

Folder 01 sampai 07 cukup Python biasa:

```bash
cd 01-ubiquitous-language
python before.py
python after.py
```

Folder 07 memakai SQLAlchemy dengan database SQLite di memory, jadi tidak ada file database yang dibuat.

## Hands-on: Modeling Domain dengan DDD Dasar

Mulai dari `08-ddd-order/before/` (hasil akhir Sesi 2), lalu perkaya domain-nya seperti di `after/`.

```
after/
├── app/
│   ├── domain/
│   │   ├── money.py             # value object Money
│   │   ├── order.py             # aggregate Order + OrderLine + OrderStatus
│   │   └── discount_policy.py   # domain service DiscountPolicy
│   ├── application/             # ports + use case: place, pay, cancel
│   ├── infrastructure/          # SQLite repository (orders + order_lines)
│   ├── api/                     # routes + dependencies
│   └── main.py
└── tests/                       # test domain, test use case, test API
```

Kriteria selesai:

- [ ] Harga dan diskon memakai value object `Money`
- [ ] Item order hanya bisa ditambah lewat `Order.add_item()`
- [ ] Order yang sudah dibayar tidak bisa dibatalkan atau diubah
- [ ] Aturan diskon ada di domain service `DiscountPolicy`
- [ ] Endpoint baru `POST /orders/{id}/pay` dan `POST /orders/{id}/cancel`
- [ ] Test domain jalan tanpa service, FastAPI, maupun database, `pytest` hijau

Kunci jawaban ada di `after/`:

```bash
cd 08-ddd-order/after
uvicorn app.main:app --reload
pytest -v
```

Contoh request:

```bash
curl -X POST localhost:8000/orders -H "Content-Type: application/json" \
  -d '{"customer": "budi@mail.com", "customer_type": "vip", "items": [{"name": "Keyboard", "price": 500000, "qty": 2}]}'
curl -X POST localhost:8000/orders/1/pay
curl -X POST localhost:8000/orders/1/cancel     # 409, order yang sudah dibayar tidak bisa dibatalkan
```

## Catatan

- Response API sekarang berisi `status`, `items`, `subtotal`, `discount`, dan `total`.
- Tabel database ikut berubah (`orders` + `order_lines`). Kalau masih ada `orders.db` dari sesi sebelumnya, hapus dulu.
- Hands-on masih memakai `sqlite3`. Pindah ke SQLAlchemy + transaksi dibahas di Sesi 4.
