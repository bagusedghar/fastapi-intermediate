"""Test API tanpa menyentuh orders.db. Jalankan: pytest -v"""
from fastapi.testclient import TestClient

from after import app, get_repository


class InMemoryOrderRepository:
    def __init__(self):
        self.rows = []

    def add(self, customer: str, total: int) -> dict:
        order = {"id": len(self.rows) + 1, "customer": customer, "total": total}
        self.rows.append(order)
        return order


def test_create_order_pakai_fake_repository():
    fake = InMemoryOrderRepository()
    app.dependency_overrides[get_repository] = lambda: fake
    client = TestClient(app)

    response = client.post("/orders", json={"customer": "budi@mail.com", "subtotal": 200_000})

    assert response.status_code == 201
    assert response.json()["total"] == 190_000
    assert len(fake.rows) == 1  # tersimpan di fake, bukan di database
    app.dependency_overrides.clear()
