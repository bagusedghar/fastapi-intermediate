"""Test API: database diganti SQLite di memory lewat dependency_overrides."""
import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_notifier, get_session_factory
from app.infrastructure.database import create_session_factory
from app.main import app
from tests.fakes import FakeNotifier


@pytest.fixture
def client():
    session_factory = create_session_factory("sqlite://")
    app.dependency_overrides[get_session_factory] = lambda: session_factory
    app.dependency_overrides[get_notifier] = FakeNotifier
    client = TestClient(app)
    client.post("/products", json={"name": "Keyboard", "price": 500_000, "stock": 5})
    client.post("/products", json={"name": "Mouse", "price": 100_000, "stock": 1})
    yield client
    app.dependency_overrides.clear()


def order(*items, customer_type="vip"):
    return {"customer": "budi@mail.com", "customer_type": customer_type,
            "items": [{"product_id": p, "qty": q} for p, q in items]}


def test_buat_order_mengurangi_stok(client):
    created = client.post("/orders", json=order((1, 2)))
    assert created.status_code == 201
    assert created.json()["total"] == 900_000
    assert client.get("/products/1").json()["stock"] == 3


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


def test_format_error_konsisten(client):
    not_found = client.get("/orders/99")
    assert not_found.status_code == 404
    assert not_found.json()["error"]["code"] == "order_not_found"

    invalid = client.post("/orders", json={"customer": "budi@mail.com", "items": []})
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "validation_error"

    unknown = client.post("/orders", json=order((1, 1), customer_type="sultan"))
    assert unknown.status_code == 400
    assert unknown.json()["error"]["code"] == "unknown_customer_type"


def test_middleware_menambah_header(client):
    assert "x-process-time" in client.get("/products").headers
