"""Test API: dependency asli diganti fake lewat dependency_overrides."""
import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_notifier, get_repository
from app.main import app
from tests.fakes import FakeNotifier, FakeOrderRepository

PAYLOAD = {"customer": "budi@mail.com", "customer_type": "vip",
           "items": [{"name": "Keyboard", "price": 500_000, "qty": 2}]}


@pytest.fixture
def client():
    repo = FakeOrderRepository()
    app.dependency_overrides[get_repository] = lambda: repo
    app.dependency_overrides[get_notifier] = FakeNotifier
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_create_lalu_get_order(client):
    created = client.post("/orders", json=PAYLOAD)
    assert created.status_code == 201
    body = created.json()
    assert (body["subtotal"], body["discount"], body["total"]) == (1_000_000, 100_000, 900_000)
    assert body["status"] == "pending"

    assert client.get(f"/orders/{body['id']}").json() == body


def test_bayar_lalu_batal_ditolak(client):
    order_id = client.post("/orders", json=PAYLOAD).json()["id"]
    paid = client.post(f"/orders/{order_id}/pay")
    assert paid.json()["status"] == "paid"
    assert client.post(f"/orders/{order_id}/cancel").status_code == 409


def test_tipe_customer_tidak_dikenal(client):
    payload = {**PAYLOAD, "customer_type": "sultan"}
    assert client.post("/orders", json=payload).status_code == 400


def test_order_tidak_ditemukan(client):
    assert client.get("/orders/99").status_code == 404
    assert client.post("/orders/99/pay").status_code == 404
