# Contoh README Fitur

Setiap fitur baru punya satu README di `docs/fitur/<nama-fitur>.md`, yang menjelaskan fitur itu dari
semua layer sekaligus. README root cukup memberi link ke file ini.

Contoh di bawah memakai fitur voucher dari studi kasus Sesi 4. Cukup singkat, sekitar satu sampai dua layar.

---

# Fitur: Voucher Diskon

Customer bisa memakai kode voucher saat membuat order untuk mendapat potongan harga tetap.
Setiap voucher punya kuota. Kuota berkurang saat dipakai dan kembali saat order dibatalkan.

## Aturan bisnis

- Satu order hanya bisa memakai satu voucher
- Voucher dengan kuota 0 tidak bisa dipakai (`voucher_exhausted`)
- Potongan voucher tidak membuat total order negatif
- Order dibatalkan = kuota voucher dikembalikan
- Stok kurang = order gagal, kuota voucher tidak terpakai (satu transaksi dengan stok)

## Endpoint

| Method | Path | Scope | Keterangan |
|---|---|---|---|
| POST | `/vouchers` | `products:write` (admin) | Buat voucher: `code`, `amount`, `quota` |
| GET | `/vouchers/{code}` | `products:write` (admin) | Detail dan sisa kuota |
| POST | `/orders` | `orders:write` | Field baru `voucher_code` (opsional) |

## Error

| Code | HTTP | Kapan |
|---|---|---|
| `voucher_not_found` | 404 | Kode voucher tidak ada |
| `voucher_exhausted` | 409 | Kuota sudah habis |
| `voucher_already_exists` | 409 | Membuat voucher dengan kode yang sudah ada |

## File yang ditambah atau diubah

| Layer | File | Perubahan |
|---|---|---|
| domain | `voucher.py` | Entity `Voucher`: `redeem()`, `restore()` |
| domain | `order.py` | `apply_voucher()`, field `voucher_code` |
| application | `order_service.py` | Pakai dan kembalikan kuota di dalam Unit of Work |
| application | `voucher_service.py` | Use case buat dan lihat voucher |
| infrastructure | `models.py`, `repositories.py` | Tabel `vouchers`, kolom `orders.voucher_code` |
| api | `routers/vouchers.py`, `schemas.py`, `errors.py` | Endpoint, schema, pemetaan error |

## Keputusan teknis

Kuota dikurangi di transaksi yang sama dengan stok, supaya order yang gagal tidak menghabiskan kuota.
Lihat [ADR 0004](../adr/0004-kuota-voucher-dalam-transaksi-order.md).

## Test

```bash
pytest tests/test_voucher.py -q
```

Yang dites: kuota berkurang sampai habis, total tidak negatif, kuota kembali saat order dibatalkan,
kuota tidak terpakai saat stok kurang, dan format error di API.
