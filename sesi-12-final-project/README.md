# Sesi 12 - Final Project: Production-Ready FastAPI System

**Chapter:** Security & Deployment

## Learning Outcome

- Mendemonstrasikan layanan FastAPI end-to-end yang modular, aman, dan memiliki aspek reliability/observability.
- Menunjukkan automated tests, Docker-based deployment, serta hasil pipeline CI/CD dan smoke test.
- Mempertanggungjawabkan keputusan arsitektur, kompromi scalability, dan langkah improvement menuju produksi.
- Mengumpulkan repository, README, architecture diagram, panduan menjalankan aplikasi, serta dokumentasi API.

## Isi Folder

| Folder | Topik | Yang dibahas |
|---|---|---|
| [`01-smoke-test`](01-smoke-test) | Smoke Test | Cek `/health/live` saja (deploy "berhasil") vs smoke test alur utama yang gagal dengan exit code 1 |
| [`02-documentation`](02-documentation) | Dokumentasi Teknis | README 5 baris vs README lengkap + diagram arsitektur + ADR |
| [`03-code-review`](03-code-review) | Code Review | Pull request "fix order" vs template pull request dengan checklist |
| [`04-production-ready`](04-production-ready) | Hands-on | `before/` (hasil Sesi 11) → `after/` (smoke test, CD ke Kubernetes, dokumentasi, template PR) |
| [`05-final-project`](05-final-project) | Final Project | `starter/` (Order API lengkap) untuk dilanjutkan: fitur baru, README per fitur, presentasi, rubrik |
| `slides/` | | Materi presentasi |

## Menjalankan Contoh

```bash
pip install -r requirements.txt
cd 01-smoke-test
python before.py
python after.py              # exit code 1: DATABASE_URL belum di-set
DATABASE_URL=postgresql://x python after.py
```

Contoh 02 dan 03 berupa file Markdown, dibaca dan dibandingkan langsung.

| Contoh | Before | After |
|---|---|---|
| 01 Smoke test | `/health/live` 200, "Deploy berhasil" | `/health/ready` 503 dan login 500, "Smoke test GAGAL", exit code 1 |
| 02 Dokumentasi | Cara menjalankan saja, tanpa konfigurasi dan arsitektur | README terstruktur, diagram komponen, alur request, ADR |
| 03 Code review | Deskripsi "fix order", review "LGTM" | Apa, kenapa, cara mengecek, checklist, komentar review yang spesifik |

## Hands-on: Order API Siap Production

Mulai dari `04-production-ready/before/` (hasil akhir Sesi 11). Salin jadi folder kerja baru `latihan/`, lalu kembangkan bersama mentor sesuai slide hands-on. Hasil akhirnya seperti `after/`.

```
after/
├── smoke_test.py                       # cek hasil deploy: health, login, database, worker
├── tests/test_smoke.py                 # smoke test juga dites
├── README.md                           # deskripsi, cara menjalankan, konfigurasi, test, deploy
├── docs/
│   ├── architecture.md                 # diagram komponen (Mermaid), layer, alur request
│   ├── deployment-checklist.md         # dicek sebelum rilis
│   └── adr/                            # 0001 clean architecture, 0002 keyset pagination, 0003 RabbitMQ
└── .github/
    ├── pull_request_template.md
    └── workflows/ci.yml                # + deploy-smoke: kind di runner, kubectl apply, smoke test
```

Kriteria selesai:

- [ ] `python smoke_test.py` lulus ke stack Compose dan ke cluster Kubernetes
- [ ] Smoke test gagal (exit code 1) jika salah satu dependency mati
- [ ] Job `deploy-smoke` di workflow: deploy ke kind, buat user smoke test, jalankan smoke test
- [ ] README, diagram arsitektur, tiga ADR, dan deployment checklist
- [ ] Template pull request
- [ ] `ruff check .` dan `pytest` hijau

Kunci jawaban ada di `after/`. Menjalankan smoke test ke Kubernetes lokal:

```bash
cd 04-production-ready/after
docker build -t order-api:1.0 .
kind load docker-image order-api:1.0 --name latihan
kubectl apply -f k8s/
kubectl exec deploy/order-api -- python create_user.py smoke@toko.com --role admin
kubectl port-forward svc/order-api 8080:80 &
BASE_URL=http://localhost:8080 SMOKE_EMAIL=smoke@toko.com SMOKE_PASSWORD=... python smoke_test.py
```

Di GitHub, tambahkan repository secret `SMOKE_PASSWORD` (Settings > Secrets and variables > Actions).

## Final Project

Final project melanjutkan Order API, bukan membuat aplikasi baru. Titik awalnya `05-final-project/starter/`
(hasil akhir hands-on Sesi 12) atau folder `latihan/` sendiri. Peserta menambahkan minimal dua fitur, README untuk
setiap fitur baru, dan dokumentasi, lalu mempresentasikannya. Detailnya di [`05-final-project/README.md`](05-final-project/README.md).

## Catatan

- Smoke test bukan pengganti pytest. pytest mengecek logika kode, smoke test mengecek hasil deploy: config, koneksi, dan dependency.
- User smoke test dibuat sekali di setiap environment, dengan password dari secret. Jangan memakai akun customer sungguhan.
- Job `deploy-smoke` memakai cluster kind yang dibuat di runner GitHub dan hilang setelah job selesai. Deploy ke cluster sungguhan memakai `kubectl` dengan kubeconfig dari secret, langkahnya sama.
- Job `publish` sekarang baru jalan setelah smoke test lulus, jadi image yang ada di registry selalu sudah dicoba di-deploy.
- Diagram di `docs/architecture.md` ditulis dengan Mermaid, dan GitHub menampilkannya sebagai gambar.
