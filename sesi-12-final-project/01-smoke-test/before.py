"""Smoke Test - BEFORE (cek manual setelah deploy)

Setelah deploy, developer hanya membuka satu URL. Jika jawabannya 200, deploy dianggap berhasil.
/health/live hanya mengecek proses berjalan, jadi masalah konfigurasi tidak terlihat.
Customer yang pertama mencoba login yang menemukan error.

Jalankan: python before.py
"""
from fastapi.testclient import TestClient

from app import app

if __name__ == "__main__":
    # anggap: httpx.Client(base_url=BASE_URL)
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/health/live")
    print(f"GET /health/live -> {response.status_code}")
    print("Deploy berhasil" if response.status_code == 200 else "Deploy gagal")
