# Studi Kasus Hari 5: Batasi Login Gagal

Dikerjakan **mandiri** setelah Sesi 9 dan Sesi 10. Gunakan materi sesi-sesi sebelumnya: Redis (Sesi 6), log terstruktur dan metrics (Sesi 9), serta login JWT dan format error (Sesi 10).

Mulai dari `before/` (sama dengan hasil hands-on Sesi 10). Kunci jawaban ada di `after/`.

## Latar Belakang

Endpoint `POST /auth/token` bisa dipanggil berulang-ulang tanpa batas. Penyerang bisa mencoba ribuan password untuk satu email sampai ketemu (**brute force**), dan tim tidak tahu sedang diserang.

Tim security meminta: setelah **5 kali login gagal** untuk email yang sama, email itu **diblokir 15 menit**. Setiap login gagal juga harus terlihat di log dan metrics.

## Requirement

- Login gagal dihitung **per email** di Redis, dengan key `v1:login-fail:<email>`.
- Gagal ke-5 dalam 15 menit: login berikutnya untuk email itu dijawab **429** dengan code `too_many_login_attempts` dan header `Retry-After` (detik). Password tidak dicek selama diblokir, walaupun benar.
- Login berhasil sebelum diblokir: hitungan kembali ke 0.
- Email yang tidak terdaftar juga dihitung, supaya penyerang tidak bisa menebak email mana yang terdaftar.
- Setiap login gagal dicatat di log WARNING `login gagal` dengan field `email` dan `failures`. **Password tidak boleh masuk log.**
- Metric baru: `login_failures_total` dan `login_blocked_total`.
- Batas dan lama blokir diatur lewat `LOGIN_MAX_ATTEMPTS` (default 5) dan `LOGIN_BLOCK_SECONDS` (default 900).
- `domain/` dan `application/` tetap tanpa `fastapi`, `redis`, dan `prometheus_client`.

## Langkah Singkat

1. Tambahkan port `LoginAttemptLimiter` di `application/ports.py`: `blocked_for(email) -> int`, `record_failure(email)`, `reset(email)`.
2. Tambahkan error `TooManyLoginAttempts(retry_after)` di `application/errors.py`.
3. Ubah `AuthService.login`: cek blokir dulu, catat kegagalan, dan reset setelah berhasil.
4. Buat `RedisLoginAttemptLimiter` di `infrastructure/login_limiter.py` (INCR + EXPIRE), lengkap dengan log dan metric.
5. Tambahkan metric di `infrastructure/metrics.py` dan setting di `config.py`.
6. Pasang limiter di `get_auth_service`, lalu tambahkan handler 429 di `api/errors.py`.
7. Tulis test: 5 kali gagal lalu diblokir, reset setelah berhasil, email tidak terdaftar, email lain tidak ikut diblokir, dan log tanpa password.

## Contoh Hasil

```
$ curl -X POST localhost:8000/auth/token -d "username=budi@mail.com&password=salah"     # 5 kali
{"error": {"code": "invalid_credentials", "message": "Email atau password salah", ...}}

$ curl -i -X POST localhost:8000/auth/token -d "username=budi@mail.com&password=<password benar>"
HTTP/1.1 429 Too Many Requests
retry-after: 897
{"error": {"code": "too_many_login_attempts", "message": "Terlalu banyak login gagal, coba lagi dalam 897 detik", ...}}
```

Log API:

```
{"level": "WARNING", "logger": "app.auth", "message": "login gagal", "email": "budi@mail.com", "failures": 5, ...}
{"level": "WARNING", "logger": "app.auth", "message": "login diblokir", "email": "budi@mail.com", ...}
```

## Kriteria Selesai

- [ ] Gagal 5 kali = login ke-6 dijawab 429 dengan `Retry-After`, walaupun password benar
- [ ] Login berhasil mereset hitungan
- [ ] Email tidak terdaftar ikut dihitung, email lain tidak ikut diblokir
- [ ] Log `login gagal` berisi email dan jumlah gagal, tanpa password
- [ ] `login_failures_total` muncul di `/metrics`
- [ ] `pytest` hijau termasuk test baru

## Menjalankan

```bash
cd sesi-10-api-security
docker compose up -d                  # PostgreSQL, Redis, RabbitMQ, Jaeger, Prometheus
cd 10-studi-kasus-login-limit/before  # atau after/ untuk kunci jawaban
cp .env.example .env                  # isi JWT_SECRET
python create_user.py budi@mail.com --type vip
uvicorn app.main:app --reload --no-access-log --env-file .env
pytest -v
```

## Catatan

- Fixed window (hitungan mulai saat gagal pertama, hilang setelah 15 menit) sudah cukup untuk kasus ini. Rate limiter sliding window dari Sesi 6 juga bisa dipakai, tetapi kuncinya email, bukan IP.
- Pemblokiran per email bisa dipakai penyerang untuk sengaja mengunci akun orang lain. Di production biasanya digabung dengan batas per IP dan CAPTCHA setelah beberapa kali gagal.
- Test memakai fakeredis, jadi tidak butuh Redis sungguhan.
