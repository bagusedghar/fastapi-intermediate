# Studi Kasus Hari 2: Voucher Belanja

Dikerjakan **mandiri** setelah Sesi 3 dan Sesi 4. Gunakan materi dua sesi tersebut: entity, aggregate, error domain, APIRouter, schema, exception handler, dan Unit of Work.

Mulai dari `before/` (sama dengan hasil hands-on Sesi 4). Kunci jawaban ada di `after/`.

## Latar Belakang

Tim marketing ingin membagikan voucher belanja, misalnya `HEMAT50` untuk potongan Rp50.000. Jumlah voucher terbatas: setiap voucher punya **kuota**, dan setiap order yang memakai voucher mengurangi kuotanya satu.

## Requirement

- Endpoint baru `POST /vouchers` untuk membuat voucher: `code`, `amount` (besar potongan), `quota`.
- Endpoint baru `GET /vouchers/{code}` untuk melihat sisa kuota.
- Request `POST /orders` punya field baru `voucher_code` (boleh kosong).
- Potongan voucher **ditambahkan** ke diskon tipe customer. Total tidak boleh di bawah Rp0.
- Mengurangi stok, mengurangi kuota voucher, dan menyimpan order ada dalam **satu Unit of Work**. Kalau stok kurang, kuota voucher tidak ikut berkurang.
- Membatalkan order mengembalikan stok **dan** kuota voucher.
- Response order menampilkan `voucher_code`.
- Error memakai format yang sama dengan Sesi 4:

| Kondisi | Status | `error.code` |
|---|---|---|
| Voucher tidak ditemukan | 404 | `voucher_not_found` |
| Kuota voucher habis | 409 | `voucher_exhausted` |
| Kode voucher sudah dipakai saat membuat voucher | 409 | `voucher_already_exists` |

## Langkah Singkat

1. Buat entity `Voucher` di `domain/voucher.py`. Kuota hanya berubah lewat `redeem()` dan `restore()`.
2. Tambahkan error domain `VoucherExhausted` dan `VoucherAlreadyExists`, serta `VoucherNotFound` di application.
3. Tambahkan `voucher_code` dan method `apply_voucher()` ke `Order`.
4. Tambahkan tabel `vouchers` (ORM model), `SqlAlchemyVoucherRepository`, dan `uow.vouchers`.
5. Buat `VoucherService`, lalu pakai voucher di `OrderService.place_order()` dan kembalikan kuotanya di `cancel_order()`.
6. Tambahkan schema, router `api/routers/vouchers.py`, dependency, dan pemetaan status code di `api/errors.py`.
7. Tulis test: domain, use case dengan fake UoW, transaksi, dan API.

## Contoh Hasil

Buat voucher:

```json
POST /vouchers
{"code": "HEMAT50", "amount": 50000, "quota": 1}
```

Pakai di order (customer vip, Keyboard 1 × Rp500.000):

```json
POST /orders
{
  "customer": "budi@mail.com",
  "customer_type": "vip",
  "items": [{"product_id": 1, "qty": 1}],
  "voucher_code": "HEMAT50"
}
```

Response `201`: `subtotal` 500000, `discount` 100000 (vip 10% + voucher), `total` 400000, `voucher_code` "HEMAT50". Order kedua dengan voucher yang sama ditolak:

```json
{"error": {"code": "voucher_exhausted", "message": "Kuota voucher HEMAT50 sudah habis", "details": null}}
```

## Kriteria Selesai

- [ ] `POST /vouchers` dan `GET /vouchers/{code}` jalan, kode dobel ditolak 409
- [ ] Potongan voucher masuk ke `discount`, total tidak pernah negatif
- [ ] Kuota berkurang saat dipakai, kembali saat order dibatalkan
- [ ] Stok kurang = kuota voucher tidak berubah (satu transaksi)
- [ ] Error voucher memakai format `{"error": {...}}` dengan code sesuai tabel
- [ ] `domain/` dan `application/` tetap tanpa `fastapi` dan `sqlalchemy`
- [ ] `pytest` hijau, termasuk test baru untuk voucher

## Menjalankan

```bash
cd 10-studi-kasus-voucher/before    # atau after/ untuk kunci jawaban
uvicorn app.main:app --reload
pytest -v
```

## Catatan

- Struktur tabel berubah (tabel `vouchers` baru, kolom `voucher_code` di `orders`). Kalau masih ada `orders.db` dari hands-on, hapus dulu filenya supaya tabel dibuat ulang.
