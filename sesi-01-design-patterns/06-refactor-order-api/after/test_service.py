"""Test service tanpa database dan tanpa server. Jalankan: pytest -v"""
import pytest

from repository import InMemoryOrderRepository
from service import OrderNotFound, OrderService


class FakeNotifier:
    def __init__(self):
        self.sent = []

    def send(self, to: str, message: str) -> None:
        self.sent.append((to, message))


def make_service():
    return OrderService(InMemoryOrderRepository(), FakeNotifier())


def test_vip_dapat_diskon_10_persen():
    service = make_service()
    order = service.place_order("budi@mail.com", "vip", [{"price": 500_000, "qty": 2}])
    assert order["subtotal"] == 1_000_000
    assert order["total"] == 900_000


def test_notifikasi_terkirim_ke_customer():
    service = make_service()
    service.place_order("budi@mail.com", "regular", [{"price": 50_000, "qty": 1}])
    assert service.notifier.sent[0][0] == "budi@mail.com"


def test_tipe_customer_tidak_dikenal():
    with pytest.raises(ValueError):
        make_service().place_order("budi@mail.com", "sultan", [{"price": 50_000, "qty": 1}])


def test_order_tidak_ditemukan():
    with pytest.raises(OrderNotFound):
        make_service().get_order(99)
