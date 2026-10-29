"""Security Misconfiguration - AFTER (setting production yang aman)

- debug mati, error tak terduga dijawab pesan umum. Detailnya hanya ditulis di log server
- /docs dan /openapi.json dimatikan jika ENV=production
- CORS hanya mengizinkan domain frontend sendiri
Setting dibaca dari environment, jadi development tetap bisa memakai /docs.

Jalankan: python after.py
"""
import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

DATABASE_URL = "postgresql://app:rahasia123@db.internal/orders"
ENV = os.getenv("ENV", "production")
FRONTEND = ["https://toko.com"]

docs = "/docs" if ENV == "development" else None
openapi = "/openapi.json" if ENV == "development" else None
app = FastAPI(docs_url=docs, redoc_url=None, openapi_url=openapi)
app.add_middleware(CORSMiddleware, allow_origins=FRONTEND,
                   allow_methods=["GET", "POST"],
                   allow_headers=["Authorization", "Content-Type"])
logger = logging.getLogger("app")


@app.exception_handler(Exception)
async def handle_bug(request: Request, exc: Exception):
    logger.error("error tidak terduga", exc_info=exc)  # detail di log
    return JSONResponse(status_code=500,
                        content={"error": "internal_error"})


@app.get("/products")
def list_products():
    # anggap: database sedang mati
    raise ConnectionError(f"gagal konek ke {DATABASE_URL}")


if __name__ == "__main__":
    logging.disable()                # demo: sembunyikan log server
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/products",
                          headers={"Origin": "https://evil.com"})
    print("GET /products ->", response.status_code)
    print("  ", response.text)
    docs = client.get("/docs", headers={"Origin": "https://evil.com"})
    print("GET /docs ->", docs.status_code)
    print("CORS untuk https://evil.com ->",
          docs.headers.get("access-control-allow-origin"))
