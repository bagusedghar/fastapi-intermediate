# Sesi 10 - API Security: OWASP Top 10 & OAuth2

**Chapter:** Security & Deployment

## Learning Outcome

- Mengidentifikasi kerentanan API umum, termasuk broken access control, injection, dan security misconfiguration.
- Mengimplementasikan OAuth2/JWT authentication dan role/scope-based authorization di FastAPI.
- Menerapkan prinsip secrets handling, input validation, dan least privilege pada API.

## Isi Folder

Setiap topik punya dua file: `before.py` (celahnya) dan `after.py` (setelah diperbaiki).

| Folder | Topik | Yang dibahas |
|---|---|---|
| [`01-broken-access-control`](01-broken-access-control) | Broken Access Control | Budi membaca order Ani hanya dengan mengganti id di URL vs cek pemilik order |
| [`02-injection`](02-injection) | Injection | SQL dari f-string (UNION membaca tabel users) vs parameter query |
| [`03-security-misconfiguration`](03-security-misconfiguration) | Security Misconfiguration | Traceback berisi password database, `/docs` terbuka, CORS `*` vs setting production |
| [`04-jwt`](04-jwt) | JWT | Token base64 yang bisa diubah jadi admin vs JWT bertanda tangan dengan `exp` |
| [`05-oauth2-bearer`](05-oauth2-bearer) | OAuth2 Bearer | Password disimpan apa adanya, "token" = email di URL vs Argon2 + `POST /token` + header Bearer |
| [`06-rbac-scopes`](06-rbac-scopes) | RBAC & Scopes | Cek role manual di setiap endpoint (ada yang terlupa) vs `Security(..., scopes=[...])` |
| [`07-secrets`](07-secrets) | Secrets | Secret di source code vs environment + `SecretStr`, gagal start jika tidak ada |
| [`08-input-validation`](08-input-validation) | Input Validation | qty negatif dan field `price` dari client diterima vs schema Pydantic ketat |
| [`09-secure-orders`](09-secure-orders) | Hands-on | `before/` (hasil Sesi 9) → `after/` (login OAuth2/JWT, hak akses per role, order hanya milik sendiri) |
| [`10-studi-kasus-login-limit`](10-studi-kasus-login-limit) | Studi Kasus | Tugas mandiri hari 5: batasi login gagal. Soal di README folder itu |
| `docker-compose.yml` | | PostgreSQL, Redis, RabbitMQ, Jaeger, dan Prometheus |
| `slides/` | | Materi presentasi |

## Persiapan

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt  # + pyjwt, pwdlib[argon2], python-multipart, pydantic-settings
docker compose up -d
```

## Menjalankan Contoh

Contoh 01-08 cukup dijalankan dengan Python, tidak butuh Docker.

```bash
cd 01-broken-access-control
python before.py
python after.py
```

Contoh hasil:

| Contoh | Before | After |
|---|---|---|
| 01 Broken access control | Budi `GET /orders/2` (milik Ani) = 200, alamat Ani terbaca | 404 untuk Budi, 200 untuk admin |
| 02 Injection | `UNION SELECT` mengembalikan email dan hash password admin | Hasil pencarian kosong |
| 03 Misconfiguration | Response 500 berisi `postgresql://app:rahasia123@...`, `/docs` 200, CORS `*` | `{"error":"internal_error"}`, `/docs` 404, CORS tidak diizinkan |
| 04 JWT | Role diubah jadi admin dan diterima | `InvalidSignatureError`, `ExpiredSignatureError` |
| 05 OAuth2 Bearer | Password terbaca, `/me?user=ani@mail.com` mengembalikan data Ani | Hash Argon2, `/me` tanpa token = 401 `WWW-Authenticate: Bearer` |
| 06 RBAC & scopes | Customer bisa `DELETE /products/1` | Customer 403 di semua endpoint admin |
| 07 Secrets | Config tercetak lengkap dengan password | Tanpa env = `Field required`, dicetak `SecretStr('**********')` |
| 08 Input validation | qty -5 = total -2.500.000, `price: 1` menimpa harga | 422 dengan pesan per field |

## Hands-on: Proteksi Endpoint dengan OAuth2/RBAC dan Security Checklist

Mulai dari `09-secure-orders/before/` (hasil akhir Sesi 9). Salin jadi folder kerja baru `latihan/`, lalu kembangkan langkah demi langkah bersama mentor sesuai slide hands-on. Hasil akhirnya seperti `after/`.

```
after/
├── app/
│   ├── domain/user.py               # User + ROLE_SCOPES (customer, admin)
│   ├── application/
│   │   ├── ports.py                 # + UserRepository, PasswordHasher, TokenService
│   │   ├── errors.py                # + InvalidCredentials, InvalidToken, AccessDenied, UserAlreadyExists
│   │   ├── auth_service.py          # CurrentUser, register, login, authenticate (cek scope)
│   │   └── order_service.py         # actor: order atas nama user login, order orang lain = 404
│   ├── infrastructure/
│   │   ├── security.py              # Argon2PasswordHasher, JwtTokenService
│   │   ├── models.py                # + tabel users
│   │   ├── repositories.py          # + SqlAlchemyUserRepository
│   │   └── config.py                # + ENV, JWT_SECRET, ACCESS_TOKEN_MINUTES, CORS_ORIGINS, check_api_settings
│   ├── api/
│   │   ├── security.py              # OAuth2PasswordBearer + get_current_user (SecurityScopes)
│   │   ├── routers/auth.py          # POST /auth/token, GET /auth/me
│   │   ├── routers/*.py             # Security(get_current_user, scopes=[...])
│   │   ├── schemas.py               # OrderIn tanpa customer, extra="forbid", batas panjang dan jumlah
│   │   └── errors.py                # 401 + WWW-Authenticate, 403
│   └── main.py                      # gagal start tanpa JWT_SECRET, /docs hanya di development, CORS
├── create_user.py                   # membuat user, password lewat getpass
├── .env.example
└── tests/                           # + test_security.py
```

| Role | Scope | Boleh |
|---|---|---|
| customer | `orders:write` | Membuat, membayar, membatalkan, dan melihat order **miliknya sendiri** |
| admin | `orders:write`, `orders:all`, `products:write`, `reports:read` | + order semua customer, tambah produk, report |

Kriteria selesai:

- [ ] `POST /auth/token` (form username + password) mengembalikan JWT, password salah = 401
- [ ] Password disimpan sebagai hash Argon2
- [ ] Endpoint order butuh login. Order dibuat atas nama user di token, `customer_type` dari data user
- [ ] Customer lain mendapat 404 untuk order yang bukan miliknya
- [ ] Tambah produk dan report hanya untuk admin (403 untuk customer)
- [ ] API gagal start jika `JWT_SECRET` kosong atau kurang dari 32 karakter
- [ ] `pytest` hijau

Kunci jawaban ada di `after/`. Menjalankan aplikasi:

```bash
cd 09-secure-orders/after
cp .env.example .env                                   # isi JWT_SECRET
python create_user.py admin@toko.com --role admin
python create_user.py budi@mail.com --type vip
uvicorn app.main:app --reload --no-access-log --env-file .env
pytest -v
```

Buka `/docs`, klik **Authorize**, lalu login dengan email dan password user yang dibuat.

## Security Checklist

| | Cek | Di Order API |
|---|---|---|
| Access control | Setiap endpoint butuh login, kecuali yang memang publik | Hanya `GET /products`, `/health/*`, `/metrics`, `/auth/token` yang publik |
| Access control | Data milik user lain tidak bisa dibaca atau diubah | `OrderService` mengecek pemilik order |
| Access control | Hak akses dari scope, dicek di satu tempat | `get_current_user` + `Security(scopes=...)` |
| Authentication | Password di-hash dengan algoritma lambat | Argon2 (pwdlib) |
| Authentication | Token punya masa berlaku dan algoritma dikunci | `exp` 30 menit, `algorithms=["HS256"]` |
| Injection | Tidak ada SQL dari f-string | SQLAlchemy dengan parameter |
| Input | Schema ketat: batas nilai, panjang, field tambahan ditolak | `extra="forbid"`, `le=100`, `max_length` |
| Input | Data penting tidak diambil dari body request | `customer` dan `customer_type` dari token |
| Secrets | Secret dari environment, tidak di-commit, tidak tercetak | `JWT_SECRET`, `.env` di `.gitignore`, `repr=False` |
| Configuration | Setting production berbeda dari development | `ENV=production` mematikan `/docs`, CORS allowlist |
| Error | Error tidak membocorkan detail internal | Pesan umum + `request_id`, detail hanya di log |
| Least privilege | User dan proses hanya punya akses yang dibutuhkan | Customer hanya `orders:write`. Consumer tidak butuh `JWT_SECRET` |
| Logging | Kejadian keamanan tercatat, tanpa data sensitif | 401/403 tercatat `error_type=client`, password tidak pernah di-log |

## Catatan

- `uvicorn --env-file .env` membaca file `.env` sebelum aplikasi di-import. Di production, environment variable diisi oleh platform deployment (dibahas di Sesi 11).
- `ENV` default `development` supaya `/docs` bisa dipakai saat latihan. Di production wajib `ENV=production`.
- `/metrics` dan `/health/*` tetap publik karena dipanggil Prometheus dan load balancer. Di production, akses ke endpoint ini dibatasi di level jaringan.
- Order milik orang lain dijawab 404, bukan 403, supaya penyerang tidak tahu id order mana yang ada.
- Pesan login salah sama untuk email tidak terdaftar dan password salah.
- JWT tidak bisa ditarik kembali sebelum `exp`. Karena itu masa berlakunya dibuat pendek. Logout dan refresh token tidak dibahas di sesi ini.
- Contoh 07 memakai `pydantic-settings`. Hands-on tetap memakai config dari Sesi 4 (dataclass + `os.getenv`) dengan pengecekan di `check_api_settings`, supaya perubahannya kecil.
- `seed.py` dan `profile_queries.py` dari Sesi 7 masih bisa dipakai. Order dari `seed.py` tidak terhubung ke user yang login.
