# Pull request #42: Batasi qty per item order maksimal 100

## Apa yang berubah
`OrderItemIn.qty` sekarang dibatasi 1 sampai 100. Request di luar batas dijawab 422. Closes #38.

## Kenapa
Ada order dengan qty 50.000 yang menghabiskan stok produk promo dalam satu request.

## Cara mengecek
1. `POST /orders` dengan `{"items": [{"product_id": 1, "qty": 1000}]}` -> 422
2. Dengan qty 2 -> 201 seperti biasa

## Checklist
- [x] Test baru: `test_qty_terlalu_besar_ditolak`
- [x] `ruff check .` dan `pytest` hijau
- [x] Tidak ada secret, password, atau token di kode maupun log
- [x] Endpoint baru punya pengecekan login dan scope (tidak ada endpoint baru)
- [x] Perubahan database punya index yang dibutuhkan (tidak ada perubahan database)
- [ ] README atau ADR diperbarui (tidak perlu)

---

Komentar reviewer di `app/api/schemas.py` baris 28:
> Batas 100 sebaiknya diambil dari config, supaya tim bisnis bisa mengubahnya tanpa deploy ulang?

Balasan:
> Setuju, saya buat issue #43 supaya pull request ini tetap kecil.
