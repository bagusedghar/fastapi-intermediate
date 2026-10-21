"""Unit test use case: tanpa FastAPI, tanpa database."""
import pytest

from app.application.order_service import OrderNotFound, OrderService
from app.domain.discount_policy import UnknownCustomerType
from app.domain.money import Money
from app.domain.order import OrderCannotBeChanged, OrderStatus
from tests.fakes import FakeNotifier, FakeOrderRepository

ITEMS = [{"name": "Keyboard", "price": 500_000, "qty": 2}]


def make_service():
    return OrderService(FakeOrderRepository(), FakeNotifier())


def test_vip_dapat_diskon_10_persen():
    order = make_service().place_order("budi@mail.com", "vip", ITEMS)
    assert order.subtotal == Money(1_000_000)
    assert order.total == Money(900_000)


def test_bayar_order():
    service = make_service()
    order = service.place_order("budi@mail.com", "regular", ITEMS)
    service.pay_order(order.id)
    assert service.get_order(order.id).status == OrderStatus.PAID
    assert service.notifier.sent[-1] == ("budi@mail.com", f"Order #{order.id} sudah dibayar")


def test_order_dibayar_tidak_bisa_dibatalkan():
    service = make_service()
    order = service.place_order("budi@mail.com", "regular", ITEMS)
    service.pay_order(order.id)
    with pytest.raises(OrderCannotBeChanged):
        service.cancel_order(order.id)


def test_tipe_customer_tidak_dikenal():
    with pytest.raises(UnknownCustomerType):
        make_service().place_order("budi@mail.com", "sultan", ITEMS)


def test_order_tidak_ditemukan():
    with pytest.raises(OrderNotFound):
        make_service().pay_order(99)
