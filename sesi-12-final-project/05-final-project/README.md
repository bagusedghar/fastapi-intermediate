# Final Project: Production-Ready FastAPI System

Final project **melanjutkan Order API** yang sudah dibangun dari Sesi 1 sampai 12, bukan membuat aplikasi
baru dari awal. Peserta menambahkan fitur sendiri, menulis dokumentasi untuk setiap fitur baru, lalu
mempresentasikan hasilnya (architecture walkthrough, live demo, dan code review).

## Titik Awal

Pilih salah satu:

- **`starter/`** di folder ini: hasil akhir hands-on Sesi 12, sudah lengkap dan semua test hijau
- **Folder `latihan/` milik sendiri** dari hands-on Sesi 12, jika semua langkahnya sudah selesai

Salin ke repository GitHub baru milik sendiri, lalu pastikan dulu semuanya jalan:

```bash
cp .env.example .env                 # isi JWT_SECRET
docker compose up -d --build
pytest -q
```

## Yang Dikerjakan

### 1. Fitur baru (minimal 2)

Bebas, asal masuk akal untuk toko online dan **menyentuh semua layer**: domain, application, infrastructure,
api, dan test. Minimal satu fitur memakai background job (Celery) **atau** event + consumer (RabbitMQ).

Contoh ide:

| Fitur | Aturan bisnis | Async / event |
|---|---|---|
| Voucher diskon | Kuota, masa berlaku, satu voucher per order | - |
| Review produk | Hanya customer yang sudah membayar order produk itu | Rata-rata rating dihitung ulang di background |
| Refund | Hanya order paid, maksimal 7 hari, stok dikembalikan | Event `order.refunded`, email ke customer |
| Wishlist | Satu produk satu kali per customer | Notifikasi saat stok kembali tersedia |
| Ongkos kirim | Tarif per kurir, gratis ongkir di atas nominal tertentu | - |
| Poin loyalty | 1 poin per Rp10.000, poin bisa dipakai sebagai potongan | Consumer dari event `order.paid` |

Fitur boleh di luar daftar ini.

### 2. README untuk setiap fitur baru

Satu fitur = satu README di `docs/fitur/<nama-fitur>.md`, yang menjelaskan fitur itu dari semua layer
sekaligus. Contohnya ada di [`contoh-readme-fitur.md`](contoh-readme-fitur.md).

```
docs/fitur/
  voucher.md       # contoh nama file
  refund.md
```

Isinya: deskripsi singkat, aturan bisnis, endpoint dan scope, error, file yang ditambah atau diubah
per layer, keputusan teknis (link ke ADR), dan cara mengetes.

### 3. Dokumentasi project

- `README.md` root: daftar fitur dengan link ke `docs/fitur/`, dan konfigurasi baru
- `docs/architecture.md`: diagram dan alur request diperbarui sesuai fitur baru
- Minimal satu ADR baru di `docs/adr/` untuk keputusan teknis di fitur baru
- Dokumentasi API: Swagger `/docs` dengan `summary` dan contoh request untuk endpoint baru

### 4. Test, deploy, dan pipeline

- Test untuk aturan bisnis dan API fitur baru, `pytest` dan `ruff check .` hijau
- `smoke_test.py` ditambah minimal satu pengecekan untuk fitur baru
- Manifest `k8s/` diperbarui jika ada config atau service baru
- Pipeline GitHub Actions hijau

## Yang Dikumpulkan

1. Link repository GitHub (public, atau private dengan akses ke mentor)
2. README root dan README setiap fitur baru (`docs/fitur/`)
3. `docs/architecture.md` dan ADR baru
4. Screenshot pipeline GitHub Actions yang hijau
5. Slide presentasi maksimal 10 halaman

## Presentasi (15 menit + 5 menit tanya jawab)

1. Fitur baru: masalah yang diselesaikan dan aturan bisnisnya (2 menit)
2. Architecture walkthrough: di layer mana saja fitur baru ditambahkan, dan alur satu request (4 menit)
3. Live demo: `docker compose up`, coba fitur baru, lalu tunjukkan log, metrics, dan trace-nya (5 menit)
4. Test, pipeline CI/CD, dan smoke test (2 menit)
5. Trade-off yang diambil dan langkah berikutnya menuju production (2 menit)

## Rubrik Penilaian

| Kriteria | Bobot | Nilai penuh jika |
|---|---|---|
| Desain dan kualitas kode fitur baru | 25% | Mengikuti layer yang ada, aturan bisnis di domain, lint bersih |
| Implementasi fitur | 20% | Kedua fitur jalan, aturan bisnis benar, error ditangani |
| Data dan reliability | 15% | Transaksi benar, index tepat, background job atau consumer aman dari pesan ganda |
| Security | 10% | Endpoint baru punya login dan scope, data user lain tidak bisa diakses |
| Testing | 10% | Test aturan bisnis dan API fitur baru, hijau di CI |
| Dokumentasi | 15% | README fitur jelas, diagram dan ADR diperbarui |
| Deployment dan presentasi | 5% | Compose, pipeline, dan smoke test berjalan, demo lancar |

## Catatan

- Kerjakan bertahap dan commit sering. Satu fitur = satu pull request, supaya pipeline CI berjalan dan
  template pull request terisi.
- Mulai dari domain: tulis aturan bisnis dan test-nya dulu, baru endpoint dan database.
- Jika ada requirement yang tidak sempat dibuat, tulis alasan dan rencananya di README. Itu lebih baik
  daripada fitur setengah jadi tanpa penjelasan.
