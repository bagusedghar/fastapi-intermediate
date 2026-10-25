"""Test API: dependency asli diganti fake lewat dependency_overrides."""
import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_notifier, get_repository
from app.main import app
from tests.fakes import FakeNotifier, FakeOrderRepository


@pytest.fixture
def client():
    repo = FakeOrderRepository()
    app.dependency_overrides[get_repository] = lambda: repo
    app.dependency_overrides[get_notifier] = FakeNotifier
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_create_lalu_get_order(client):
    payload = {"customer": "budi@mail.com", "customer_type": "vip",
               "items": [{"name": "Keyboard", "price": 500_000, "qty": 2}]}
    created = client.post("/orders", json=payload)
    assert created.status_code == 201
    assert created.json()["total"] == 900_000

    fetched = client.get(f"/orders/{created.json()['id']}")
    assert fetched.json() == created.json()


def test_tipe_customer_tidak_dikenal(client):
    payload = {"customer": "x", "customer_type": "sultan", "items": [{"name": "a", "price": 1, "qty": 1}]}
    assert client.post("/orders", json=payload).status_code == 400


def test_order_tidak_ditemukan(client):
    assert client.get("/orders/99").status_code == 404


def test_order_dengan_kurir(client):
    payload = {"customer": "budi@mail.com", "customer_type": "regular", "courier": "jne",
               "items": [{"name": "Mouse", "price": 100_000, "qty": 2}]}
    created = client.post("/orders", json=payload).json()
    assert (created["courier"], created["shipping_cost"], created["total"]) == ("jne", 15_000, 215_000)
    assert client.get(f"/orders/{created['id']}").json() == created


def test_kurir_tidak_dikenal(client):
    payload = {"customer": "x", "courier": "gojek", "items": [{"name": "a", "price": 1, "qty": 1}]}
    response = client.post("/orders", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Kurir tidak dikenal"
