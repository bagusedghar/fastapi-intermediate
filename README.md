# Intermediate Backend Developer with FastAPI

Materi dan source code program **Intermediate Backend Developer with FastAPI** (Hacktiv8): 12 sesi × 3 jam.

Seluruh sesi memakai satu tema yang terus berkembang, yaitu **Order Management API**: produk, order dengan
diskon per tipe customer, pembayaran, report, dan notifikasi. Setiap sesi menambahkan kemampuan baru pada
aplikasi yang sama, mulai dari kode di satu file sampai berjalan di Kubernetes dengan pipeline CI/CD.

## Peta Sesi

| Sesi | Chapter | Topik | Yang ditambahkan ke Order API | Folder |
|---|---|---|---|---|
| 1 | Software Architecture & Design Patterns | Python Design Patterns for Backend | Factory, Singleton, Strategy, Repository, Service Layer | [`sesi-01-design-patterns`](sesi-01-design-patterns) |
| 2 | Software Architecture & Design Patterns | SOLID, Clean Architecture & Dependency Injection | Layer domain, application, infrastructure, api | [`sesi-02-solid-clean-architecture`](sesi-02-solid-clean-architecture) |
| 3 | Software Architecture & Design Patterns | Domain-Driven Design Fundamentals | Order aggregate, Money value object, aturan bayar dan batal | [`sesi-03-domain-driven-design`](sesi-03-domain-driven-design) |
| 4 | Scalable FastAPI Applications | Modular FastAPI & ORM Transactions | Router per modul, SQLAlchemy, Unit of Work, format error | [`sesi-04-modular-fastapi-orm-transactions`](sesi-04-modular-fastapi-orm-transactions) |
| 5 | Scalable FastAPI Applications | Asynchronous Tasks with Celery & Redis | Notifikasi dan report di background job | [`sesi-05-async-tasks-celery-redis`](sesi-05-async-tasks-celery-redis) |
| 6 | Scalable FastAPI Applications | Redis Caching, Rate Limiting & API Gateway | Cache produk, rate limit | [`sesi-06-redis-caching-rate-limiting`](sesi-06-redis-caching-rate-limiting) |
| 7 | Data & System Reliability | Database Optimization, Replication & Sharding | PostgreSQL, index, tanpa N+1, keyset pagination | [`sesi-07-database-optimization`](sesi-07-database-optimization) |
| 8 | Data & System Reliability | Event-Driven Architecture, RabbitMQ & Kafka | Event order, consumer notifikasi yang retry-safe | [`sesi-08-event-driven-rabbitmq-kafka`](sesi-08-event-driven-rabbitmq-kafka) |
| 9 | Data & System Reliability | Observability: Logging, Monitoring & Tracing | Log JSON, metrics, health check, tracing | [`sesi-09-observability`](sesi-09-observability) |
| 10 | Security & Deployment | API Security: OWASP Top 10 & OAuth2 | Login OAuth2/JWT, hak akses per role | [`sesi-10-api-security`](sesi-10-api-security) |
| 11 | Security & Deployment | Docker, Kubernetes Basics & CI/CD Pipeline | Docker image, Compose, Kubernetes, GitHub Actions | [`sesi-11-docker-kubernetes-cicd`](sesi-11-docker-kubernetes-cicd) |
| 12 | Security & Deployment | Final Project: Production-Ready FastAPI System | Smoke test, CD, dokumentasi, brief final project | [`sesi-12-final-project`](sesi-12-final-project) |

Studi kasus mandiri ada di akhir setiap hari (Sesi 2, 4, 6, 8, 10). Final project melanjutkan Order API dari
`sesi-12-final-project/05-final-project/starter/` dengan fitur baru dan README per fitur.

## Struktur Setiap Sesi

```
sesi-XX-topik/
├── README.md          # learning outcome, cara menjalankan contoh, hands-on, catatan
├── requirements.txt
├── slides/            # materi presentasi (.pptx)
├── 01-topik/          # contoh per topik: before & after
├── 02-topik/
├── 0X-hands-on/       # before/ (titik awal) & after/ (hasil akhir + test)
└── 0Y-studi-kasus/    # sesi genap: soal mandiri di README, before/ & after/
```

Hands-on dikerjakan di folder kerja baru `latihan/` (salinan `before/`), langkah demi langkah sesuai slide.
Folder `before/` setiap sesi sama dengan `after/` sesi sebelumnya.

## Kebutuhan

- Python 3.11+ dan Git
- Docker Desktop / Docker Engine (mulai Sesi 5)
- Cluster Kubernetes lokal: kind, minikube, atau Kubernetes bawaan Docker Desktop (Sesi 11-12)
- Akun GitHub (Sesi 11-12)
- Windows: disarankan memakai WSL2

## Lisensi

Materi ini disusun untuk keperluan pembelajaran di Hacktiv8.
