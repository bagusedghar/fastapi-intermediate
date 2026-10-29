# Sesi 9 - Observability: Logging, Monitoring & Tracing

**Chapter:** Data & System Reliability

## Learning Outcome

- Menghasilkan log terstruktur yang dapat ditelusuri menggunakan request/correlation ID.
- Menentukan metrics utama untuk traffic, latency, errors, serta membuat health/readiness checks.
- Membaca alur request antar komponen melalui distributed traces untuk troubleshooting.

## Isi Folder

Setiap topik punya dua file: `before.py` (masalahnya) dan `after.py` (setelah konsepnya diterapkan).

| Folder | Topik | Yang dibahas |
|---|---|---|
| [`01-structured-logging`](01-structured-logging) | Structured Logging | Log kalimat bebas vs satu baris JSON dengan field `order_id`, `customer` |
| [`02-correlation-id`](02-correlation-id) | Correlation ID | Log dari banyak request bercampur vs `request_id` di setiap log dan header `X-Request-ID` |
| [`03-error-classification`](03-error-classification) | Klasifikasi Error | Semua error 500 + ERROR vs client (WARNING), dependency (503), bug (traceback) |
| [`04-metrics`](04-metrics) | Metrics | Rata-rata waktu response vs Prometheus counter dan histogram per route |
| [`05-health-checks`](05-health-checks) | Health Checks | `/health` selalu ok vs liveness dan readiness yang mengecek database dan Redis |
| [`06-sli-alerting`](06-sli-alerting) | SLI, SLO & Alerting | Alert untuk setiap error vs alert saat SLI di bawah SLO |
| [`07-tracing`](07-tracing) | Distributed Tracing | Hanya total waktu vs span OpenTelemetry yang tersambung sampai consumer |
| [`08-observability`](08-observability) | Hands-on | `before/` (hasil Sesi 8) → `after/` (log JSON, metrics, health check, tracing di Order API) |
| `docker-compose.yml` | | PostgreSQL, Redis, RabbitMQ, Jaeger, dan Prometheus |
| `prometheus/` | | Konfigurasi scrape dan alert rule SLO |
| `slides/` | | Materi presentasi |

## Persiapan

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
docker compose up -d             # PostgreSQL :5432, Redis :6379, RabbitMQ :5672, Jaeger :16686, Prometheus :9090
```

- Jaeger (trace): http://localhost:16686
- Prometheus (metrics dan alert): http://localhost:9090
- Dashboard RabbitMQ: http://localhost:15672 (user `guest`, password `guest`)

## Menjalankan Contoh

Contoh 01-07 cukup dijalankan dengan Python, tidak butuh Docker.

```bash
cd 02-correlation-id
python before.py
python after.py
```

Contoh hasil:

| Contoh | Before | After |
|---|---|---|
| 01 Structured logging | Cari teks "order #2": 1 dari 3 log | Filter `order_id == 2`: 3 dari 3 log |
| 02 Correlation ID | Log "event gagal dikirim" tidak jelas milik request mana | Setiap log punya `request_id`, sama dengan header `X-Request-ID` |
| 03 Klasifikasi error | 4 log ERROR, semua response 500 | 2 WARNING (client), 1 ERROR dependency (503), 1 ERROR bug dengan lokasi kode (500) |
| 04 Metrics | Rata-rata 17 ms, terlihat cepat | Histogram: 5 request di atas 250 ms, 4 request status 500 |
| 05 Health checks | `/health` 200 padahal `/products` 500 | `/health/live` 200, `/health/ready` 503 karena Redis mati |
| 06 SLI & alerting | 9 alert dari 3 window | 1 alert, hanya di window yang latency-nya di bawah SLO |
| 07 Tracing | "selesai dalam 471 ms", tanpa rincian | Pohon span: `rabbitmq.publish` 400 ms, sampai span consumer dengan trace_id yang sama |

## Hands-on: Request Logging, Metrics Endpoint, dan Tracing untuk FastAPI

Mulai dari `08-observability/before/` (hasil akhir Sesi 8). Salin jadi folder kerja baru `latihan/`, lalu kembangkan langkah demi langkah bersama mentor sesuai slide hands-on. Hasil akhirnya seperti `after/`.

```
after/
├── app/
│   ├── infrastructure/
│   │   ├── logs.py          # JsonFormatter, RequestContextFilter (request_id + trace_id), setup_logging
│   │   ├── metrics.py       # http_requests_total, http_request_duration_seconds, events, notifikasi
│   │   ├── health.py        # check_database, check_redis, check_rabbitmq
│   │   ├── tracing.py       # OpenTelemetry: FastAPI + SQLAlchemy, kirim ke Jaeger
│   │   ├── rabbitmq.py      # + span publish, traceparent di header pesan
│   │   └── config.py        # + LOG_LEVEL, TRACING_ENABLED, OTEL_EXPORTER_OTLP_ENDPOINT, CONSUMER_METRICS_PORT
│   ├── api/
│   │   ├── middleware.py    # request_id, access log JSON, metrics per route
│   │   ├── errors.py        # klasifikasi error: client / dependency / bug, request_id di body error
│   │   ├── routers/ops.py   # /health/live, /health/ready, /metrics
│   │   └── dependencies.py  # + get_health_checks
│   ├── consumers/
│   │   └── notification_consumer.py   # span consumer tersambung ke trace API, metrics di port 8001
│   └── main.py              # setup_logging, setup_tracing
└── tests/                   # + test_observability.py
```

Kriteria selesai:

- [ ] Setiap log berupa satu baris JSON dan membawa `request_id` dan `trace_id`
- [ ] Response membawa header `X-Request-ID`, body error membawa `request_id` yang sama
- [ ] Error dicatat dengan `error_type`: client (WARNING), dependency (503), bug (500 + traceback)
- [ ] `GET /metrics` menampilkan jumlah request dan waktu response per route
- [ ] `GET /health/ready` mengembalikan 503 jika database, Redis, atau RabbitMQ mati. `GET /health/live` tetap 200
- [ ] Satu trace di Jaeger berisi request API, query database, publish event, dan consumer notifikasi
- [ ] `pytest` hijau tanpa Docker

Kunci jawaban ada di `after/`. Menjalankan aplikasi, masing-masing di terminal sendiri:

```bash
cd 08-observability/after
python -m app.consumers.notification_consumer
celery -A app.worker.celery_app worker --loglevel=info --pool=solo
uvicorn app.main:app --reload --no-access-log
pytest -v
```

Lalu buat beberapa order lewat `/docs`, dan lihat hasilnya:

- Log JSON di terminal uvicorn dan consumer
- http://localhost:8000/metrics dan http://localhost:8001/metrics
- http://localhost:8000/health/ready, lalu coba `docker compose stop redis`
- Jaeger: pilih service `order-api`, klik trace `POST /orders`
- Prometheus: menu **Status > Targets** (API dan consumer harus UP) dan menu **Alerts**

Contoh log API:

```
{"time": "...", "level": "INFO", "logger": "app.access", "message": "request selesai", "method": "POST", "route": "/orders", "status": 201, "duration_ms": 156.5, "request_id": "de40ddc2...", "trace_id": "7f235d2a..."}
```

## Catatan

- `--no-access-log` mematikan access log bawaan uvicorn, karena middleware sudah mencatat setiap request dalam format JSON.
- Label `route` di metrics memakai pola path (`/orders/{order_id}`), bukan path asli (`/orders/7`). Path asli membuat jumlah kombinasi label terus bertambah dan memberatkan Prometheus.
- Liveness sengaja tidak mengecek dependency. Jika Redis mati, me-restart API tidak memperbaikinya. Readiness yang memberi tahu load balancer untuk berhenti mengirim traffic.
- Prometheus berjalan di Docker dan mengambil metrics dari API di laptop lewat `host.docker.internal`. Jika target terlihat DOWN, pastikan uvicorn dan consumer sedang berjalan.
- Alert rule ada di `prometheus/alerts.yml`. Di production, alert yang aktif diteruskan oleh Alertmanager ke Slack, email, atau PagerDuty.
- Trace dikirim dengan `BatchSpanProcessor`, jadi baru muncul di Jaeger beberapa detik setelah request selesai.
- `TRACING_ENABLED=0` mematikan pengiriman trace, dipakai di test.
- `SQLAlchemyInstrumentor` dipanggil dengan `skip_dep_check=True`, karena library instrumentation belum mencantumkan SQLAlchemy 2.1 sebagai versi yang didukung.
