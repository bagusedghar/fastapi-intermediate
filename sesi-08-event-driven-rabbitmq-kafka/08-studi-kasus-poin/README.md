# Studi Kasus Hari 4: Poin Loyalty dari Event

Dikerjakan **mandiri** setelah Sesi 7 dan Sesi 8. Gunakan materi sesi-sesi sebelumnya: event, exchange dan binding, ack/nack, dead letter queue, idempotent consumer, port dan adapter, serta transaksi database.

Mulai dari `before/` (sama dengan hasil hands-on Sesi 8). Kunci jawaban ada di `after/`.

## Latar Belakang

Tim marketing ingin memberi **poin loyalty** kepada customer: setiap order yang sudah dibayar memberi **1 poin per Rp10.000** dari total order. Poin ini tidak boleh membuat pembayaran lebih lambat, dan tidak boleh bertambah dua kali walaupun event-nya datang dua kali.

Karena `OrderService` sudah mengumumkan event `order.paid` ke RabbitMQ, fitur ini cukup ditambahkan sebagai **consumer baru**. Kode `OrderService` tidak perlu diubah.

## Requirement

- Queue baru `points`, di-bind ke exchange `orders` dengan routing key `order.paid`. Pesan rusak masuk ke `points.dlq`.
- Consumer baru `python -m app.consumers.points_consumer`:
  - Event `order.paid`: tambah poin customer sebesar `total // 10_000`.
  - Event lain yang masuk ke queue ini diabaikan, lalu di-ack.
  - Pesan rusak (bukan JSON, field kurang, `total` bukan angka): `nack(requeue=False)`, masuk DLQ.
  - Ack manual dan `prefetch_count=1`.
- **Idempotent**: event dengan `event_id` yang sama hanya menambah poin sekali. Pencatatan `event_id` dan penambahan poin ada dalam **satu transaksi** database.
- Endpoint baru `GET /customers/{customer}/points`, berisi `customer` dan `points`. Customer yang belum punya poin = 0.
- Consumer notifikasi tetap berjalan seperti sebelumnya.
- `domain/` dan `application/` tetap tanpa `fastapi`, `sqlalchemy`, dan `pika`.

## Langkah Singkat

1. Tambahkan port `PointsLedger` di `application/ports.py`: `add(event_id, customer, points) -> bool` dan `balance(customer) -> int`.
2. Buat `PointsService` di `application/points_service.py`: validasi event, hitung poin, dan abaikan event selain `order.paid`.
3. Tambahkan tabel `customer_points` dan `point_events` di `infrastructure/models.py`.
4. Buat `SqlAlchemyPointsLedger` di `infrastructure/points_ledger.py`. Simpan `event_id` dan tambah poin dalam satu transaksi. `IntegrityError` artinya event sudah pernah diproses.
5. Tambahkan queue `points` dan `points.dlq` di `declare_topology` (`infrastructure/rabbitmq.py`).
6. Buat consumer `app/consumers/points_consumer.py`, polanya sama dengan consumer notifikasi.
7. Tambahkan schema `PointsOut`, dependency `get_points_service`, dan router `api/routers/customers.py`.
8. Tulis test: perhitungan poin, event yang datang dua kali, event selain `order.paid`, pesan rusak, dan API.

## Contoh Hasil

Order vip Keyboard 2 × Rp500.000 (total Rp900.000 setelah diskon) dibayar. Log consumer poin:

```
INFO Menunggu event di queue points ...
INFO event 6f1c...: added
```

```
GET /customers/budi@mail.com/points

{"customer": "budi@mail.com", "points": 90}
```

## Kriteria Selesai

- [ ] Queue `points` hanya menerima event `order.paid`
- [ ] Order yang dibayar menambah poin `total // 10_000`
- [ ] Event yang sama dikirim ulang tidak menambah poin lagi
- [ ] Pesan rusak masuk `points.dlq`, tidak di-retry
- [ ] `GET /customers/{customer}/points` menampilkan saldo poin
- [ ] `OrderService` tidak diubah, `pytest` hijau termasuk test baru

## Menjalankan

```bash
cd sesi-08-event-driven-rabbitmq-kafka
docker compose up -d                  # PostgreSQL, Redis, RabbitMQ
cd 08-studi-kasus-poin/before         # atau after/ untuk kunci jawaban
python -m app.consumers.points_consumer
uvicorn app.main:app --reload
pytest -v
```

## Catatan

- Tabel baru dibuat otomatis oleh `create_all` saat aplikasi atau consumer dijalankan.
- `pytest` tidak butuh RabbitMQ. Keputusan ack/nack consumer dites dengan `FakeChannel`, sama seperti test consumer notifikasi.
- Jika database mati saat consumer berjalan, consumer berhenti tanpa ack. Pesan tetap di queue dan diproses lagi saat consumer dijalankan ulang.
