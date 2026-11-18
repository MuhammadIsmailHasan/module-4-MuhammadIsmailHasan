import os

import pytest

os.environ.setdefault("ALLOWED_ORIGINS", "http://localhost:3000")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret-0REMOVED9abcdef0123")
os.environ.setdefault("FILE_URL_SECRET", "test-file-secret-0REMOVED9abcdef01")
os.environ.setdefault("APP_TIMEZONE", "UTC")
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app  # noqa: E402
from app.extensions import db  # noqa: E402


@pytest.fixture
def app(tmp_path):
    app = create_app({"TESTING": True, "UPLOAD_DIR": str(tmp_path / "uploads")})
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


class FakeRepository:
    """Base for in-memory fake repositories used by service unit tests."""

    def __init__(self):
        self.rows = {}

    def add(self, row):
        self.rows[row.id] = row
        return row

    def get_by_id(self, id_):
        return self.rows.get(id_)


@pytest.fixture
def fake_repository():
    return FakeRepository


@pytest.fixture
def make_user(app):
    from argon2 import PasswordHasher

    from app.models import User

    hasher = PasswordHasher()

    def _make(role="member", login=None):
        login = login or f"{role}-{User.query.count()}@example.com"
        user = User(full_name=role.title(), login_identifier=login, password_hash=hasher.hash("REMOVED"), role=role)
        db.session.add(user)
        db.session.commit()
        return user

    return _make


@pytest.fixture
def auth(app):
    from app.common.auth import issue_token

    def _auth(user):
        return {"Authorization": f"Bearer {issue_token(user.id, user.role)}"}

    return _auth
