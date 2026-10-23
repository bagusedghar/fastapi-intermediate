# Sesi 8 - Event-Driven Architecture, RabbitMQ & Kafka

**Chapter:** Data & System Reliability

## Learning Outcome

- Menentukan kapan menggunakan synchronous API call vs asynchronous message-based integration.
- Membangun event producer dan consumer sederhana dengan RabbitMQ, acknowledgement, dan failure handling.
- Menjelaskan konsep dasar Kafka serta perbedaan karakteristik penggunaan Kafka dan RabbitMQ.

## Isi Folder

Setiap topik punya dua file: `before.py` (masalahnya) dan `after.py` (setelah konsepnya diterapkan).

| Folder | Topik | Yang dibahas |
|---|---|---|
| [`01-sync-vs-async`](01-sync-vs-async) | Sync vs Async | Semua layanan dipanggil langsung vs producer-consumer lewat antrean |
| [`02-exchange-queue`](02-exchange-queue) | Exchange & Queue | Producer kirim langsung ke setiap queue vs topic exchange + binding |
| [`03-ack`](03-ack) | Acknowledgement | `auto_ack` (pesan hilang saat crash) vs ack manual + `prefetch_count` |
| [`04-nack-dead-letter`](04-nack-dead-letter) | Nack & Dead Letter Queue | Requeue tanpa henti vs retry dengan jeda + dead letter queue |
| [`05-idempotent-consumer`](05-idempotent-consumer) | Idempotent Consumer | Pesan dobel = poin dobel vs `event_id` dicatat dalam transaksi yang sama |
| [`06-kafka-basics`](06-kafka-basics) | Kafka | RabbitMQ: event hilang setelah di-ack vs Kafka: topic, partition, consumer group, offset |
| [`07-event-driven-orders`](07-event-driven-orders) | Hands-on | `before/` (hasil Sesi 7) → `after/` (event order lewat RabbitMQ, consumer notifikasi yang retry-safe) |
| `docker-compose.yml` | | PostgreSQL, Redis, RabbitMQ, dan Kafka |
| `slides/` | | Materi presentasi |

## Persiapan

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
docker compose up -d             # PostgreSQL :5432, Redis :6379, RabbitMQ :5672, Kafka :9092
```

Dashboard RabbitMQ ada di http://localhost:15672 (user `guest`, password `guest`). Di tab **Queues** terlihat isi setiap queue, termasuk dead letter queue.

## Menjalankan Contoh

Contoh 01 tidak butuh apa-apa, contoh 02-05 butuh RabbitMQ, contoh 06 butuh RabbitMQ (`before.py`) dan Kafka (`after.py`).

```bash
cd 03-ack
python before.py
python after.py
```

Contoh hasil:

| Contoh | Before | After |
|---|---|---|
| 01 Sync vs async | 1151 ms, response 500 karena analytics mati | 50 ms, response 201, analytics gagal di consumer saja |
| 02 Exchange & queue | Queue analytics tidak ada sampai producer diubah | Queue baru cukup di-bind ke exchange `orders` |
| 03 Ack | Crash di order #2, sisa di queue 0 (order #2 dan #3 hilang) | Sisa di queue 2, diproses ulang setelah consumer jalan lagi |
| 04 Nack & DLQ | Pesan rusak diproses 12.763 kali dalam 3 detik, order #2 tidak pernah diproses | Pesan rusak langsung ke DLQ, order #2 berhasil di percobaan ke-3 |
| 05 Idempotent consumer | Poin 180 (seharusnya 90) | Poin 90, pesan kedua di-skip |
| 06 Kafka | Consumer baru menerima 0 event | Consumer group baru membaca 6 event dari offset 0 |

## Hands-on: Publish/Consume Event FastAPI dengan RabbitMQ

Mulai dari `07-event-driven-orders/before/` (hasil akhir Sesi 7), lalu kembangkan seperti di `after/`.

```
after/
├── app/
│   ├── application/
│   │   ├── events.py                 # order_event(): event_id, type, order_id, customer, total
│   │   ├── ports.py                  # + EventPublisher, NotificationLog
│   │   ├── order_service.py          # publish event setelah commit, tidak lagi memanggil Notifier
│   │   └── notification_service.py   # kirim notifikasi dari event, idempotent lewat event_id
│   ├── infrastructure/
│   │   ├── config.py                 # + RABBITMQ_URL, NOTIFICATION_MAX_RETRIES, NOTIFICATION_RETRY_DELAY_MS
│   │   └── rabbitmq.py               # topologi (exchange, queue, retry, DLQ) + RabbitMQPublisher
│   ├── consumers/
│   │   └── notification_consumer.py  # ack/nack, retry dengan jeda, DLQ
│   ├── api/dependencies.py           # get_event_publisher
│   └── worker/tasks.py               # tinggal report, notifikasi pindah ke consumer
└── tests/                            # + test_notification_consumer.py
```

Kriteria selesai:

- [ ] `OrderService` mengumumkan `order.placed`, `order.paid`, `order.cancelled` setelah commit, lewat port `EventPublisher`
- [ ] Event dikirim ke exchange `orders` (topic), queue `notifications` di-bind dengan `order.*`
- [ ] Consumer memakai ack manual dan `prefetch_count=1`
- [ ] Gangguan sementara di-retry dengan jeda yang makin panjang. Pesan rusak dan pesan yang melewati batas retry masuk `notifications.dlq`
- [ ] Event yang datang dua kali tidak membuat notifikasi dobel (idempotent lewat `event_id`)
- [ ] `pytest` hijau tanpa RabbitMQ

Kunci jawaban ada di `after/`. Menjalankan aplikasi, masing-masing di terminal sendiri:

```bash
cd 07-event-driven-orders/after
python -m app.consumers.notification_consumer
celery -A app.worker.celery_app worker --loglevel=info --pool=solo
uvicorn app.main:app --reload
pytest -v
```

Mencoba retry dan dead letter queue: jalankan consumer dengan server email yang sering gagal, lalu buat beberapa order lewat `/docs`.

```bash
# PowerShell: $env:NOTIFICATION_FAIL_RATE="0.5"; python -m app.consumers.notification_consumer
NOTIFICATION_FAIL_RATE=0.5 python -m app.consumers.notification_consumer
```

Contoh log consumer:

```
INFO event b612337a-...: sent
WARNING Server email timeout, retry ke-1 dalam 1000 ms
INFO event 3503d9d3-...: retrying
WARNING Server email timeout, retry ke-2 dalam 2000 ms
INFO event 3503d9d3-...: sent
ERROR [ALERT] Gagal 4 kali, dipindah ke DLQ: Server email timeout
```

## Catatan

- Event di-publish setelah commit. Kalau RabbitMQ mati tepat setelah order tersimpan, request tetap berhasil (201) tetapi event-nya hilang dan tercatat di log API. Solusi lengkapnya adalah outbox pattern: event disimpan ke tabel dalam transaksi yang sama dengan order, lalu dikirim oleh proses terpisah.
- Exchange, queue, dan binding dideklarasikan oleh API dan consumer (`declare_topology`), jadi urutan menjalankannya tidak penting.
- Jeda retry memakai expiration per pesan di queue `notifications.retry`. Setelah kedaluwarsa, pesan otomatis kembali ke queue `notifications`.
- Retry bisa mengubah urutan notifikasi. Contohnya, notifikasi "sudah dibayar" bisa sampai lebih dulu daripada "order dibuat" kalau yang kedua sedang di-retry.
- Celery tetap dipakai untuk report. Notifikasi pindah ke consumer RabbitMQ karena ini reaksi atas event, bukan job yang diminta user.
- Consumer berhenti kalau koneksi ke RabbitMQ putus. Jalankan ulang, pesan yang belum di-ack tidak hilang. Restart otomatis dibahas di sesi deployment.
- `seed.py` dan `profile_queries.py` dari Sesi 7 masih ada dan tetap bisa dipakai.
- Contoh 02-06 menghapus lalu membuat ulang queue dan topic yang dipakainya, supaya hasilnya selalu sama setiap dijalankan. Nama queue di contoh (`email`, `points`, `analytics`) berbeda dengan queue hands-on (`notifications`).
