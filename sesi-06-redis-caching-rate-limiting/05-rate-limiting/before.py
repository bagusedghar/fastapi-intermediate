"""Rate Limiting - BEFORE

Tidak ada batas request. Satu client (atau bot) bisa mengirim ratusan request per detik,
menghabiskan resource server dan membuat client lain ikut lambat.

Jalankan demo: python before.py
Atau server:   uvicorn before:app --reload
"""
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()


@app.post("/orders", status_code=201)
def create_order():
    return {"message": "Order dibuat"}


if __name__ == "__main__":
    client = TestClient(app)
    codes = [client.post("/orders").status_code for _ in range(15)]
    print("Status code:", codes)                    # 15x 201, semua diterima
