"""Test ongkos kirim: aturan domain dan use case, tanpa FastAPI dan tanpa database."""
import pytest

from app.application.order_service import OrderService
from app.domain.shipping import UnknownCourier, get_courier
from tests.fakes import FakeNotifier, FakeOrderRepository


def make_service():
    return OrderService(FakeOrderRepository(), FakeNotifier())


@pytest.mark.parametrize("courier, expected", [("pickup", 0), ("jne", 15_000), ("sicepat", 12_000)])
def test_ongkir_per_kurir(courier, expected):
    assert get_courier(courier).cost(100_000) == expected


def test_gratis_ongkir_mulai_500_ribu():
    assert get_courier("jne").cost(499_999) == 15_000
    assert get_courier("jne").cost(500_000) == 0


def test_kurir_tidak_dikenal():
    with pytest.raises(UnknownCourier):
        get_courier("gojek")


def test_total_termasuk_ongkir():
    order = make_service().place_order("budi@mail.com", "regular", [{"price": 100_000, "qty": 2}], "jne")
    assert (order.subtotal, order.shipping_cost, order.total) == (200_000, 15_000, 215_000)


def test_gratis_ongkir_dihitung_setelah_diskon():
    # subtotal 550.000, diskon vip 10% = 495.000 -> belum gratis ongkir
    order = make_service().place_order("budi@mail.com", "vip", [{"price": 550_000, "qty": 1}], "sicepat")
    assert (order.shipping_cost, order.total) == (12_000, 507_000)
