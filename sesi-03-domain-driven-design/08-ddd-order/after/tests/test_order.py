"""Unit test domain: murni Python, tanpa service, FastAPI, maupun database."""
import pytest

from app.domain.money import Money
from app.domain.order import Order, OrderCannotBeChanged, OrderStatus


def make_order() -> Order:
    order = Order("budi@mail.com", "vip")
    order.add_item("Keyboard", Money(500_000), 2)
    return order


def test_money_tidak_boleh_negatif():
    with pytest.raises(ValueError):
        Money(-1)


def test_total_dihitung_dari_item_dan_diskon():
    order = make_order()
    order.apply_discount(Money(100_000))
    assert order.subtotal == Money(1_000_000)
    assert order.total == Money(900_000)


def test_diskon_tidak_boleh_melebihi_subtotal():
    with pytest.raises(ValueError):
        make_order().apply_discount(Money(2_000_000))


def test_order_dibayar_tidak_bisa_dibatalkan():
    order = make_order()
    order.pay()
    assert order.status == OrderStatus.PAID
    with pytest.raises(OrderCannotBeChanged):
        order.cancel()


def test_item_tidak_bisa_ditambah_setelah_dibayar():
    order = make_order()
    order.pay()
    with pytest.raises(OrderCannotBeChanged):
        order.add_item("Mouse", Money(100_000), 1)


def test_order_kosong_tidak_bisa_dibayar():
    with pytest.raises(OrderCannotBeChanged):
        Order("budi@mail.com", "regular").pay()
