"""Smoke Test - AFTER (cek otomatis alur utama setelah deploy)

Smoke test = beberapa pengecekan singkat ke aplikasi yang BARU di-deploy, memakai request sungguhan.
Bukan pengganti pytest: yang dicek adalah hasil deploy (config, koneksi, dependency), bukan logika kode.
- Setiap langkah dicetak OK atau GAGAL
- Satu langkah gagal = exit code 1, jadi pipeline CD berhenti dan versi lama bisa dikembalikan

Jalankan: python after.py
Di production: BASE_URL=https://api.toko.com python smoke_test.py
"""
import sys

from fastapi.testclient import TestClient

from app import app

# anggap: httpx.Client(base_url=BASE_URL)
client = TestClient(app, raise_server_exceptions=False)
LOGIN = {"username": "budi@mail.com", "password": "rahasia123"}

CHECKS = [
    ("proses berjalan", "GET", "/health/live", {}),
    ("dependency siap", "GET", "/health/ready", {}),
    ("login berhasil", "POST", "/auth/token", {"params": LOGIN}),
]


def run() -> bool:
    ok = True
    for name, method, path, kwargs in CHECKS:
        response = client.request(method, path, **kwargs)
        passed = response.status_code < 400
        ok = ok and passed
        status = "OK   " if passed else "GAGAL"
        print(f"{status} {name:<16} {method} {path} -> "
              f"{response.status_code}")
    return ok


if __name__ == "__main__":
    passed = run()
    print("Smoke test lulus" if passed
          else "Smoke test GAGAL, deploy dihentikan")
    sys.exit(0 if passed else 1)
