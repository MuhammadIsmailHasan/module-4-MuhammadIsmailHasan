from app.extensions import db
from app.models import User


def test_seed_refuses_outside_dev_and_testing(make_app):
    app = make_app("production")
    with app.app_context():
        db.create_all()
        result = app.test_cli_runner().invoke(args=["seed-users"])
        assert result.exit_code != 0 and "development or testing" in result.output
        assert User.query.count() == 0


def test_seed_uses_env_password_or_generates_one(make_app, monkeypatch):
    app = make_app("testing")
    with app.app_context():
        db.create_all()
        monkeypatch.delenv("SEED_PASSWORD", raising=False)
        out = app.test_cli_runner().invoke(args=["seed-users"]).output
        assert "Generated password (shown once)" in out
        assert User.query.count() == 4
        assert all(u.password_hash.startswith("$argon2") for u in User.query.all())
