# Sesi 5 - Asynchronous Tasks with Celery & Redis

**Chapter:** Scalable FastAPI Applications

## Learning Outcome

- Membedakan async request processing dari background worker untuk beban kerja berdurasi panjang.
- Menghubungkan FastAPI, Celery, dan Redis untuk memproses job secara asynchronous.
- Menerapkan retry, idempotency, serta penanganan task failure dan status monitoring.

## Isi Folder

Setiap topik punya dua file: `before.py` (masalahnya) dan `after.py` (setelah konsepnya diterapkan).

| Folder | Topik | Yang dibahas |
|---|---|---|
| [`01-async-io`](01-async-io) | Async IO | `time.sleep` di `async def` memblok request lain, `await` tidak |
| [`02-background-tasks`](02-background-tasks) | Background Job | Email dikirim di dalam request vs `BackgroundTasks` setelah response |
| [`03-celery`](03-celery) | Celery | Report dibuat di proses API vs dikirim ke worker lewat Redis |
| [`04-task-status`](04-task-status) | Task Status | Status di dict (tidak pernah berubah) vs `AsyncResult` dari result backend |
| [`05-retry-timeout`](05-retry-timeout) | Retry & Timeout | `autoretry_for`, `retry_backoff`, `max_retries`, `soft_time_limit`, `time_limit` |
| [`06-idempotency`](06-idempotency) | Idempotency | Retry membuat email terkirim dua kali vs idempotency key |
| [`07-failure-handling`](07-failure-handling) | Failure Handling | Error hanya di-print (status SUCCESS) vs `on_failure` dan daftar failed jobs |
| [`08-async-jobs`](08-async-jobs) | Hands-on | `before/` (hasil Sesi 4) → `after/` (notifikasi & report lewat Celery) |
| `docker-compose.yml` | | Redis untuk broker dan result backend |
| `slides/` | | Materi presentasi |

## Persiapan

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
docker compose up -d             # menjalankan Redis di localhost:6379
```

## Menjalankan Contoh

Folder 01, 05, 06, dan 07 cukup Python biasa. Contoh Celery di 05-07 memakai mode eager (task langsung dijalankan), jadi tidak perlu Redis.

```bash
cd 05-retry-timeout
python before.py
python after.py
```

Folder 02 memakai FastAPI:

```bash
cd 02-background-tasks
uvicorn before:app --reload
uvicorn after:app --reload
```

Folder 03 dan 04 butuh Redis, worker, dan API. Jalankan masing-masing di terminal sendiri:

```bash
cd 04-task-status
celery -A after:celery_app worker --loglevel=info --pool=solo
uvicorn after:app --reload
```

Lalu buka http://127.0.0.1:8000/docs, panggil `POST /reports/sales`, dan cek `GET /reports/{task_id}` beberapa kali.

## Hands-on: Asynchronous Job untuk Email & Report

Mulai dari `08-async-jobs/before/` (hasil akhir Sesi 4). Salin jadi folder kerja baru `latihan/`, lalu kembangkan langkah demi langkah bersama mentor sesuai slide hands-on. Hasil akhirnya seperti `after/`.

```
after/
├── app/
│   ├── domain/            # tidak berubah
│   ├── application/       # + report_service.py, OrderService tidak berubah
│   ├── infrastructure/    # + notification_log.py, config Celery, simulasi email gangguan
│   ├── worker/
│   │   ├── celery_app.py  # konfigurasi Celery
│   │   ├── tasks.py       # send_notification, generate_sales_report
│   │   ├── notifier.py    # QueuedNotifier: adapter Notifier lewat queue
│   │   └── jobs.py        # mulai job & baca status
│   ├── api/routers/       # + reports.py
│   └── main.py
└── tests/                 # + test_tasks.py (retry, idempotency, failure)
```

Kriteria selesai:

- [ ] Notifikasi order dikirim lewat Celery, response API tidak menunggu email
- [ ] `OrderService` tidak berubah, cukup adapter `Notifier`-nya yang diganti
- [ ] `POST /reports/sales` menjawab 202 dengan `task_id`, report dibuat oleh worker
- [ ] `GET /reports/{task_id}` menampilkan status `pending` / `running` / `done` / `failed` dan hasilnya
- [ ] Notifikasi di-retry dengan backoff saat server email gangguan
- [ ] Notifikasi yang sama tidak terkirim dua kali (idempotency key)
- [ ] Task yang gagal permanen tercatat di log worker, `pytest` hijau

Kunci jawaban ada di `after/`. Jalankan masing-masing di terminal sendiri:

```bash
cd 08-async-jobs/after
celery -A app.worker.celery_app worker --loglevel=info --pool=solo
uvicorn app.main:app --reload
pytest -v
```

Contoh request:

```bash
curl -X POST localhost:8000/products -H "Content-Type: application/json" \
  -d '{"name": "Keyboard", "price": 500000, "stock": 5}'
curl -X POST localhost:8000/orders -H "Content-Type: application/json" \
  -d '{"customer": "budi@mail.com", "customer_type": "vip", "items": [{"product_id": 1, "qty": 2}]}'
curl -X POST localhost:8000/reports/sales          # {"task_id": "...", "status_url": "/reports/..."}
curl localhost:8000/reports/<task_id>              # pending -> running -> done
```

## Catatan

- `--pool=solo` diperlukan supaya worker Celery jalan di Windows. Di Linux/Mac boleh dihapus.
- `soft_time_limit` dan `time_limit` tidak aktif di `--pool=solo`. Untuk melihatnya bekerja, jalankan worker di Linux/Mac atau di Docker.
- Untuk melihat retry, set `NOTIFICATION_FAIL_RATE=0.5` sebelum menjalankan worker (setengah percobaan kirim email gagal). Di PowerShell: `$env:NOTIFICATION_FAIL_RATE="0.5"`. Log retry dan `[ALERT]` muncul di terminal worker.
- Lama pembuatan report diatur lewat `REPORT_DELAY` (default 5 detik).
- `pytest` tidak butuh Redis. Test memakai `CELERY_TASK_ALWAYS_EAGER=1`, jadi task langsung dijalankan di dalam test (lihat `tests/conftest.py`).
- Task ID yang tidak dikenal tetap berstatus `pending`, karena Celery tidak bisa membedakan "belum diambil worker" dengan "tidak pernah ada".
