"""Test pembatas login gagal (Redis diganti fakeredis lewat fixture fake_redis di conftest.py)."""
import logging

from prometheus_client import REGISTRY

from tests.conftest import PASSWORD


def login(client, email, password):
    return client.post("/auth/token", data={"username": email, "password": password})


def fail(client, email, times):
    for _ in range(times):
        assert login(client, email, "salah").status_code == 401


def test_lima_kali_gagal_lalu_diblokir(client):
    fail(client, "budi@mail.com", 5)
    response = login(client, "budi@mail.com", PASSWORD)          # password benar pun ditolak
    assert response.status_code == 429
    assert response.json()["error"]["code"] == "too_many_login_attempts"
    assert 0 < int(response.headers["Retry-After"]) <= 900


def test_login_berhasil_mereset_hitungan(client):
    fail(client, "budi@mail.com", 4)
    assert login(client, "budi@mail.com", PASSWORD).status_code == 200
    fail(client, "budi@mail.com", 4)
    assert login(client, "budi@mail.com", PASSWORD).status_code == 200


def test_email_tidak_terdaftar_juga_dihitung(client):
    fail(client, "tidakada@mail.com", 5)
    assert login(client, "tidakada@mail.com", "salah").status_code == 429


def test_email_lain_tidak_ikut_diblokir(client):
    fail(client, "budi@mail.com", 5)
    assert login(client, "ani@mail.com", PASSWORD).status_code == 200


def test_blokir_berakhir_setelah_window(client, fake_redis):
    fail(client, "budi@mail.com", 5)
    assert 0 < fake_redis.ttl("v1:login-fail:budi@mail.com") <= 900
    fake_redis.delete("v1:login-fail:budi@mail.com")               # anggap: 15 menit sudah lewat
    assert login(client, "budi@mail.com", PASSWORD).status_code == 200


def test_login_gagal_dicatat_tanpa_password(client, caplog):
    with caplog.at_level(logging.WARNING, logger="app.auth"):
        login(client, "budi@mail.com", "password-rahasia-salah")
    record = next(r for r in caplog.records if r.name == "app.auth")
    assert record.getMessage() == "login gagal"
    assert record.email == "budi@mail.com"
    assert "password-rahasia-salah" not in str(vars(record))


def test_metric_login_gagal_bertambah(client):
    before = REGISTRY.get_sample_value("login_failures_total") or 0
    fail(client, "budi@mail.com", 2)
    assert REGISTRY.get_sample_value("login_failures_total") == before + 2
