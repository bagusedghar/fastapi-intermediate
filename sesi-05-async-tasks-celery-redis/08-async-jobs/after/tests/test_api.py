"""Test API: Celery berjalan eager, jadi notifikasi dan report langsung dikerjakan di dalam test."""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    client = TestClient(app)
    client.post("/products", json={"name": "Keyboard", "price": 500_000, "stock": 5})
    client.post("/products", json={"name": "Mouse", "price": 100_000, "stock": 1})
    return client


def order(*items, customer_type="vip"):
    return {"customer": "budi@mail.com", "customer_type": customer_type,
            "items": [{"product_id": p, "qty": q} for p, q in items]}


def test_buat_order_mengurangi_stok_dan_mengirim_notifikasi(client, capsys):
    created = client.post("/orders", json=order((1, 2)))
    assert created.status_code == 201
    assert created.json()["total"] == 900_000
    assert client.get("/products/1").json()["stock"] == 3
    assert "[EMAIL] ke budi@mail.com: Order #1 total Rp900,000" in capsys.readouterr().out


def test_stok_kurang_semua_dibatalkan(client):
    response = client.post("/orders", json=order((1, 2), (2, 3)))
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "out_of_stock"
    assert client.get("/products/1").json()["stock"] == 5


def test_cancel_mengembalikan_stok_lalu_bayar_ditolak(client):
    order_id = client.post("/orders", json=order((1, 2))).json()["id"]
    assert client.post(f"/orders/{order_id}/cancel").json()["status"] == "cancelled"
    assert client.get("/products/1").json()["stock"] == 5
    assert client.post(f"/orders/{order_id}/pay").json()["error"]["code"] == "order_cannot_be_changed"


def test_report_penjualan_lewat_background_job(client):
    paid = client.post("/orders", json=order((1, 2))).json()["id"]
    client.post(f"/orders/{paid}/pay")
    cancelled = client.post("/orders", json=order((2, 1))).json()["id"]
    client.post(f"/orders/{cancelled}/cancel")

    job = client.post("/reports/sales")
    assert job.status_code == 202

    status = client.get(job.json()["status_url"]).json()
    assert status["status"] == "done"
    assert status["result"] == {"total_orders": 2, "paid_orders": 1, "cancelled_orders": 1, "revenue": 900_000}


def test_format_error_konsisten(client):
    not_found = client.get("/orders/99")
    assert not_found.status_code == 404
    assert not_found.json()["error"]["code"] == "order_not_found"

    invalid = client.post("/orders", json={"customer": "budi@mail.com", "items": []})
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "validation_error"


def test_middleware_menambah_header(client):
    assert "x-process-time" in client.get("/products").headers
