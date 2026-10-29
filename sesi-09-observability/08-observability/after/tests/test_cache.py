"""Test cache produk: cache-aside di ProductService dan invalidation setelah commit."""
from app.application.cache_keys import PRODUCT_LIST_KEY, product_key
from app.application.product_service import ProductService
from app.domain.money import Money
from app.domain.product import Product
from tests.conftest import order
from tests.fakes import FakeCache, FakeUnitOfWork


def test_cache_hit_tidak_query_database():
    uow = FakeUnitOfWork([Product("Keyboard", Money(500_000), 5)])
    queries = []
    query = uow.products.get
    uow.products.get = lambda product_id: queries.append(product_id) or query(product_id)

    service = ProductService(uow, FakeCache())
    for _ in range(3):
        assert service.get_product(1).stock == 5
    assert queries == [1]                      # cuma request pertama yang ke database


def test_produk_disimpan_di_redis_dengan_ttl(client, fake_redis):
    client.get("/products/1")
    assert fake_redis.exists(product_key(1))
    assert 0 < fake_redis.ttl(product_key(1)) <= 66      # TTL 60 + jitter maksimal 6


def test_order_menghapus_cache_produk(client, fake_redis):
    assert client.get("/products/1").json()["stock"] == 5
    assert client.get("/products").json()[0]["stock"] == 5

    client.post("/orders", json=order((1, 2)))
    assert not fake_redis.exists(product_key(1), PRODUCT_LIST_KEY)
    assert client.get("/products/1").json()["stock"] == 3
    assert client.get("/products").json()[0]["stock"] == 3


def test_order_gagal_tidak_mengubah_cache(client, fake_redis):
    client.get("/products/1")
    assert client.post("/orders", json=order((1, 2), (2, 3))).status_code == 409   # rollback
    assert fake_redis.exists(product_key(1))
    assert client.get("/products/1").json()["stock"] == 5
