# Studi Kasus Hari 1: Tambah Ongkos Kirim

Dikerjakan **mandiri** setelah Sesi 1 dan Sesi 2. Gunakan materi dua sesi tersebut: Strategy, Factory, SOLID, Clean Architecture, dan Dependency Injection.

Mulai dari `before/` (sama dengan hasil hands-on Sesi 2). Kunci jawaban ada di `after/`.

## Latar Belakang

Saat ini Order API hanya menghitung diskon. Tim bisnis ingin customer bisa memilih cara pengiriman, dan ongkos kirimnya ikut masuk ke total order.

## Requirement

| Kurir | Ongkos kirim |
|---|---|
| `pickup` (ambil sendiri, default) | Rp0 |
| `jne` | Rp15.000 |
| `sicepat` | Rp12.000 |

- Request `POST /orders` punya field baru `courier`. Kalau tidak diisi, dianggap `pickup`.
- **Gratis ongkir** kalau belanja setelah diskon minimal Rp500.000.
- `total` = subtotal - diskon + ongkos kirim.
- Response `POST /orders` dan `GET /orders/{id}` menampilkan `courier` dan `shipping_cost`.
- Kurir yang tidak dikenal ditolak dengan status **400** dan pesan `Kurir tidak dikenal`.
- Aturan arsitektur tetap berlaku: `domain/` dan `application/` tidak boleh import `fastapi` maupun `sqlite3`.
- Menambah kurir baru nanti **tidak boleh** mengubah `OrderService` (Open/Closed).

## Langkah Singkat

1. Buat aturan ongkir di layer domain, satu class per cara kirim (Strategy), lengkap dengan function untuk memilih kurir.
2. Tambahkan `courier` dan `shipping_cost` ke `Order`.
3. Hitung ongkir di `OrderService.place_order()` setelah diskon.
4. Simpan dua kolom baru di `SqliteOrderRepository`.
5. Tambahkan `courier` ke request body dan ubah error kurir tidak dikenal menjadi HTTP 400.
6. Tulis test: ongkir per kurir, gratis ongkir, kurir tidak dikenal, dan test API.

## Contoh Hasil

Request:

```json
{
  "customer": "budi@mail.com",
  "customer_type": "regular",
  "courier": "jne",
  "items": [{"name": "Mouse", "price": 100000, "qty": 2}]
}
```

Response `201`:

```json
{
  "customer": "budi@mail.com",
  "customer_type": "regular",
  "courier": "jne",
  "subtotal": 200000,
  "shipping_cost": 15000,
  "total": 215000,
  "id": 1
}
```

## Kriteria Selesai

- [ ] Ongkir sesuai tabel, gratis ongkir mulai Rp500.000 setelah diskon
- [ ] Kurir tidak dikenal → 400 `Kurir tidak dikenal`
- [ ] `courier` dan `shipping_cost` tersimpan, `GET /orders/{id}` mengembalikan data yang sama
- [ ] `domain/` dan `application/` tetap tanpa `fastapi` dan `sqlite3`
- [ ] Kurir baru cukup ditambah di file aturan ongkir, `OrderService` tidak diubah
- [ ] `pytest` hijau, termasuk test baru untuk ongkir

## Menjalankan

```bash
cd 08-studi-kasus-ongkir/before    # atau after/ untuk kunci jawaban
uvicorn app.main:app --reload
pytest -v
```

## Catatan

- Struktur tabel `orders` berubah (ada kolom `courier` dan `shipping_cost`). Kalau masih ada `orders.db` dari hands-on, hapus dulu filenya supaya tabel dibuat ulang.
