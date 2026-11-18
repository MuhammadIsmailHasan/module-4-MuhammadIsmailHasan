import pytest

from app import create_app

BASE = {
    "ALLOWED_ORIGINS": "http://a.test, http://b.test",
    "JWT_SECRET": "x" * 40,
    "FILE_URL_SECRET": "y" * 40,
    "APP_TIMEZONE": "Asia/Jakarta",
    "DATABASE_URL": "sqlite:///:memory:",
}


def _env(monkeypatch, **over):
    for k, v in {**BASE, **over}.items():
        if v is None:
            monkeypatch.delenv(k, raising=False)
        else:
            monkeypatch.setenv(k, v)


@pytest.mark.parametrize("name", ["ALLOWED_ORIGINS", "JWT_SECRET", "FILE_URL_SECRET", "APP_TIMEZONE"])
def test_missing_required_var_fails(monkeypatch, name):
    _env(monkeypatch, **{name: None})
    with pytest.raises(RuntimeError):
        create_app()


def test_wildcard_origin_fails(monkeypatch):
    _env(monkeypatch, ALLOWED_ORIGINS="*")
    with pytest.raises(RuntimeError):
        create_app()


def test_bad_timezone_fails(monkeypatch):
    _env(monkeypatch, APP_TIMEZONE="Not/AZone")
    with pytest.raises(RuntimeError):
        create_app()


def test_origins_parsed(monkeypatch):
    _env(monkeypatch)
    assert create_app().config["ALLOWED_ORIGINS"] == ["http://a.test", "http://b.test"]
