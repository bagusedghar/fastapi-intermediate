"""Test voucher: domain, use case (fake UoW), transaksi (SQLite di memory), dan API."""
import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_notifier, get_session_factory
from app.application.errors import VoucherNotFound
from app.application.order_service import OrderService
from app.application.product_service import ProductService
from app.application.voucher_service import VoucherService
from app.domain.errors import OutOfStock, VoucherExhausted
from app.domain.money import Money
from app.domain.product import Product
from app.domain.voucher import Voucher
from app.infrastructure.database import create_session_factory
from app.infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from app.main import app
from tests.fakes import FakeNotifier, FakeUnitOfWork

KEYBOARD = [{"product_id": 1, "qty": 1}]


# ---------- domain ----------
def test_redeem_mengurangi_kuota_sampai_habis():
    voucher = Voucher("HEMAT50", Money(50_000), 1)
    voucher.redeem()
    assert voucher.quota == 0
    with pytest.raises(VoucherExhausted):
        voucher.redeem()


# ---------- use case (fake UoW) ----------
def make_service(quota=2):
    uow = FakeUnitOfWork([Product("Keyboard", Money(500_000), 5), Product("Mouse", Money(100_000), 1)],
                         [Voucher("HEMAT50", Money(50_000), quota)])
    return OrderService(uow, FakeNotifier()), uow


def test_voucher_menambah_diskon_dan_mengurangi_kuota():
    service, uow = make_service()
    order = service.place_order("budi@mail.com", "vip", KEYBOARD, "HEMAT50")
    assert order.discount == Money(100_000)          # 10% vip (50.000) + voucher 50.000
    assert order.total == Money(400_000)
    assert uow.vouchers.get("HEMAT50").quota == 1


def test_potongan_voucher_tidak_membuat_total_negatif():
    service, uow = make_service()
    uow.vouchers.add(Voucher("GRATIS", Money(1_000_000), 1))
    order = service.place_order("budi@mail.com", "regular", [{"product_id": 2, "qty": 1}], "GRATIS")
    assert order.total == Money(0)


def test_voucher_tidak_ditemukan():
    service, _ = make_service()
    with pytest.raises(VoucherNotFound):
        service.place_order("budi@mail.com", "regular", KEYBOARD, "NGASAL")


def test_cancel_mengembalikan_kuota():
    service, uow = make_service()
    order = service.place_order("budi@mail.com", "regular", KEYBOARD, "HEMAT50")
    service.cancel_order(order.id)
    assert uow.vouchers.get("HEMAT50").quota == 2


# ---------- transaksi (SQLAlchemy sungguhan) ----------
def test_stok_kurang_kuota_voucher_tidak_terpakai():
    uow = SqlAlchemyUnitOfWork(create_session_factory("sqlite://"))
    ProductService(uow).create_product("Keyboard", 500_000, 5)
    ProductService(uow).create_product("Mouse", 100_000, 1)
    VoucherService(uow).create_voucher("HEMAT50", 50_000, 1)

    with pytest.raises(OutOfStock):
        OrderService(uow, FakeNotifier()).place_order(
            "budi@mail.com", "regular", [{"product_id": 2, "qty": 3}], "HEMAT50")
    assert VoucherService(uow).get_voucher("HEMAT50").quota == 1


# ---------- API ----------
@pytest.fixture
def client():
    session_factory = create_session_factory("sqlite://")
    app.dependency_overrides[get_session_factory] = lambda: session_factory
    app.dependency_overrides[get_notifier] = FakeNotifier
    client = TestClient(app)
    client.post("/products", json={"name": "Keyboard", "price": 500_000, "stock": 5})
    client.post("/vouchers", json={"code": "HEMAT50", "amount": 50_000, "quota": 1})
    yield client
    app.dependency_overrides.clear()


def order(voucher_code):
    return {"customer": "budi@mail.com", "customer_type": "vip", "items": KEYBOARD, "voucher_code": voucher_code}


def test_api_order_dengan_voucher(client):
    created = client.post("/orders", json=order("HEMAT50"))
    assert created.status_code == 201
    assert (created.json()["total"], created.json()["voucher_code"]) == (400_000, "HEMAT50")
    assert client.get("/vouchers/HEMAT50").json()["quota"] == 0


def test_api_error_voucher(client):
    client.post("/orders", json=order("HEMAT50"))
    habis = client.post("/orders", json=order("HEMAT50"))
    assert habis.status_code == 409
    assert habis.json()["error"]["code"] == "voucher_exhausted"

    tidak_ada = client.post("/orders", json=order("NGASAL"))
    assert tidak_ada.status_code == 404
    assert tidak_ada.json()["error"]["code"] == "voucher_not_found"

    dobel = client.post("/vouchers", json={"code": "HEMAT50", "amount": 10_000, "quota": 1})
    assert dobel.status_code == 409
    assert dobel.json()["error"]["code"] == "voucher_already_exists"
