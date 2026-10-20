"""Unit test use case: tanpa FastAPI, tanpa database."""
import pytest

from app.application.order_service import OrderNotFound, OrderService
from app.domain.discounts import UnknownCustomerType
from tests.fakes import FakeNotifier, FakeOrderRepository


def make_service():
    return OrderService(FakeOrderRepository(), FakeNotifier())


def test_vip_dapat_diskon_10_persen():
    order = make_service().place_order("budi@mail.com", "vip", [{"price": 500_000, "qty": 2}])
    assert order.subtotal == 1_000_000
    assert order.total == 900_000


def test_notifikasi_terkirim():
    service = make_service()
    service.place_order("budi@mail.com", "regular", [{"price": 50_000, "qty": 1}])
    assert service.notifier.sent[0][0] == "budi@mail.com"


def test_tipe_customer_tidak_dikenal():
    with pytest.raises(UnknownCustomerType):
        make_service().place_order("budi@mail.com", "sultan", [{"price": 50_000, "qty": 1}])


def test_order_tidak_ditemukan():
    with pytest.raises(OrderNotFound):
        make_service().get_order(99)
