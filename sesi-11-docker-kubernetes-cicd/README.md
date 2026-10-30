# Sesi 11 - Docker, Kubernetes Basics & CI/CD Pipeline

**Chapter:** Security & Deployment

## Learning Outcome

- Membuat Docker image dan menjalankan stack FastAPI beserta dependensinya secara lokal menggunakan Compose.
- Memahami resource Kubernetes dasar dan menyiapkan manifest Deployment/Service dengan readiness/liveness probes.
- Merancang pipeline CI/CD sederhana untuk automated test, build, dan deployment.

## Isi Folder

| Folder | Topik | Yang dibahas |
|---|---|---|
| [`01-dockerfile`](01-dockerfile) | Dockerfile | `COPY . .` di awal, secret ikut masuk image, root vs urutan layer, `.dockerignore`, user biasa |
| [`02-multi-stage`](02-multi-stage) | Multi-stage Build | Compiler ikut ke image (726 MB) vs stage builder terpisah (278 MB) |
| [`03-docker-compose`](03-docker-compose) | Docker Compose | `docker run` manual dengan `localhost` vs satu `compose.yaml` dengan healthcheck |
| [`04-deployment-service`](04-deployment-service) | Deployment & Service | Pod tunggal yang hilang saat dihapus vs Deployment 2 replica + Service |
| [`05-configmap-secret`](05-configmap-secret) | ConfigMap & Secret | API key di manifest Deployment vs ConfigMap + Secret lewat `envFrom` |
| [`06-probes`](06-probes) | Readiness & Liveness Probes | Pod langsung Ready dan tidak pernah di-restart vs probe dari endpoint Sesi 9 |
| [`07-ci-pipeline`](07-ci-pipeline) | CI Pipeline | Workflow yang hanya `pytest` setelah merge vs lint → test → build → scan → publish |
| [`k8s-demo-app`](k8s-demo-app) | | Aplikasi kecil untuk contoh 04-06 |
| [`08-dockerize-ci`](08-dockerize-ci) | Hands-on | `before/` (hasil Sesi 10) → `after/` (Dockerfile, Compose, manifest Kubernetes, GitHub Actions) |
| `slides/` | | Materi presentasi |

## Persiapan

- Docker Desktop (Windows/macOS) atau Docker Engine (Linux)
- Cluster Kubernetes lokal, pilih salah satu: [kind](https://kind.sigs.k8s.io/), [minikube](https://minikube.sigs.k8s.io/), atau Kubernetes bawaan Docker Desktop
- `kubectl`

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
kind create cluster --name latihan    # atau: minikube start
```

Image yang di-build di laptop perlu dimasukkan ke cluster lokal:

```bash
kind load docker-image k8s-demo:1.0 --name latihan       # kind
minikube image load k8s-demo:1.0                          # minikube
# Docker Desktop Kubernetes: tidak perlu, image lokal langsung terbaca
```

## Menjalankan Contoh

```bash
# 01-02: dari folder contoh
docker build -f before.Dockerfile -t demo:before .
docker build -f after.Dockerfile -t demo:after .

# 03
sh before.sh
docker compose up -d --build

# 04-06: build image demo sekali, lalu apply manifest
docker build -t k8s-demo:1.0 k8s-demo-app
kubectl apply -f 04-deployment-service/after/
kubectl get pods

# 07: langkah pipeline dijalankan di laptop
ruff check .
pytest -q
```

Contoh hasil:

| Contoh | Before | After |
|---|---|---|
| 01 Dockerfile | `whoami` = root, `.env.local` terbaca, `pip install` diulang setiap kode berubah | `appuser`, `.env.local` tidak ada, `pip install` CACHED |
| 02 Multi-stage | 726 MB, gcc ada di image | 278 MB, gcc tidak ada |
| 03 Compose | `database` dan `redis` down (localhost = container API sendiri) | Semua healthy, `/health/ready` ok |
| 04 Deployment | Pod dihapus = aplikasi hilang | Pod dihapus = dibuat ulang, Service membagi request ke 2 pod |
| 05 ConfigMap & Secret | `API_KEY` terbaca di manifest Deployment | Deployment hanya menyebut nama ConfigMap dan Secret |
| 06 Probes | `1/1 Ready` saat aplikasi belum siap, `RESTARTS 0` saat macet | `0/1` sampai siap, `RESTARTS 1` setelah macet |
| 07 CI | Hanya pytest, lolos walaupun ada import tidak terpakai | `ruff` menolak (F401), lalu test, build, dan scan Trivy |

## Hands-on: Dockerize FastAPI dan Pipeline CI

Mulai dari `08-dockerize-ci/before/` (hasil akhir Sesi 10). Salin jadi folder kerja baru `latihan/`, lalu kembangkan langkah demi langkah bersama mentor sesuai slide hands-on. Hasil akhirnya seperti `after/`.

```
after/
├── Dockerfile                 # multi-stage, user biasa (uid 10001), satu image untuk api/worker/consumer
├── .dockerignore              # .env, tests, k8s, cache tidak ikut ke image
├── requirements.txt           # dependency runtime (masuk image)
├── requirements-dev.txt       # + pytest, fakeredis, ruff (CI saja)
├── pyproject.toml             # konfigurasi ruff
├── docker-compose.yml         # api, worker, consumer, postgres, redis, rabbitmq, jaeger
├── k8s/
│   ├── config.yaml            # ConfigMap + Secret (latihan)
│   ├── api.yaml               # Deployment 2 replica + probes + resources + Service
│   ├── workers.yaml           # worker Celery + consumer notifikasi
│   └── dependencies.yaml      # postgres, redis, rabbitmq untuk cluster latihan
└── .github/workflows/ci.yml   # lint -> test -> build-scan -> publish (ghcr.io)
```

Kriteria selesai:

- [ ] `docker build` menghasilkan image yang berjalan sebagai user biasa, tanpa `.env` dan tanpa folder tests
- [ ] `docker compose up -d --build` menjalankan API, worker, dan consumer. Semua service healthy
- [ ] Login, buat order, dan report berjalan di dalam container
- [ ] `kubectl apply -f k8s/` membuat 2 pod API yang Ready, dicek lewat readiness probe
- [ ] Workflow CI menjalankan lint, test, build, dan scan
- [ ] `ruff check .` dan `pytest` hijau

Kunci jawaban ada di `after/`. Menjalankan:

```bash
cd 08-dockerize-ci/after
cp .env.example .env                                     # isi JWT_SECRET
docker compose up -d --build
docker compose exec api python create_user.py admin@toko.com --role admin
docker compose ps

# Kubernetes
docker build -t order-api:1.0 .
kind load docker-image order-api:1.0 --name latihan
kubectl apply -f k8s/
kubectl get pods
kubectl exec deploy/order-api -- python create_user.py budi@mail.com --type vip
kubectl port-forward svc/order-api 8080:80               # lalu buka http://localhost:8080/health/ready
```

## Catatan

- Satu image dipakai untuk API, worker, dan consumer. Bedanya hanya `command`. Image yang sama di semua environment membuat hasil test di CI sama dengan yang berjalan di production.
- `postgres` di Compose memakai volume `pgdata`, jadi data tetap ada setelah `docker compose down`. Hapus dengan `docker compose down -v`.
- Di Kubernetes, consumer bisa restart beberapa kali saat RabbitMQ belum siap. Kubernetes me-restart-nya otomatis sampai terhubung.
- `k8s/dependencies.yaml` hanya untuk latihan. Database di production memakai layanan managed atau StatefulSet dengan PersistentVolume.
- Secret Kubernetes hanya di-encode base64. Akses ke Secret dibatasi dengan RBAC Kubernetes, dan isinya dibuat dari luar repository.
- Workflow GitHub Actions harus berada di root repository (`.github/workflows/`). Di repository ini file-nya ada di dalam folder hands-on sebagai contoh. Salin ke root repository project sendiri supaya jalan.
- Job `publish` mendorong image ke GitHub Container Registry (`ghcr.io`) memakai `GITHUB_TOKEN`, tanpa secret tambahan.
- Contoh 06 butuh sekitar 1 menit untuk melihat restart: aplikasi demo baru siap setelah 20 detik dan macet setelah 45 detik.
