"""Security Misconfiguration - BEFORE (setting development terbawa ke production)

- debug=True   : error dikirim ke client lengkap dengan traceback, termasuk pesan yang berisi password database
- /docs terbuka: siapa pun bisa melihat semua endpoint, termasuk endpoint admin
- CORS "*"     : website mana pun boleh memanggil API dari browser user

Jalankan: python before.py
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

DATABASE_URL = "postgresql://app:rahasia123@db.internal/orders"

app = FastAPI(debug=True)
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])


@app.get("/products")
def list_products():
    # anggap: database sedang mati
    raise ConnectionError(f"gagal konek ke {DATABASE_URL}")


if __name__ == "__main__":
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/products",
                          headers={"Origin": "https://evil.com"})
    print("GET /products ->", response.status_code)
    print("  ...", "\n  ".join(response.text.splitlines()[-2:]))
    docs = client.get("/docs", headers={"Origin": "https://evil.com"})
    print("GET /docs ->", docs.status_code)
    print("CORS untuk https://evil.com ->",
          docs.headers.get("access-control-allow-origin"))
