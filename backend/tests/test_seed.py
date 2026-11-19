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


def test_seed_data_fills_every_table_and_is_idempotent(make_app, monkeypatch):
    from app.extensions import db as _db
    from app.models import (ActivityLog, Attachment, Board, BoardMember, Card, Category, Column,
                            Comment, Notification, Subtask)

    app = make_app("testing")
    with app.app_context():
        _db.create_all()
        monkeypatch.delenv("SEED_PASSWORD", raising=False)
        runner = app.test_cli_runner()
        assert "Seeded demo data" in runner.invoke(args=["seed-data"]).output
        for model in (User, Board, BoardMember, Column, Category, Card, Subtask, Attachment, Comment, ActivityLog, Notification):
            assert model.query.count() > 0, model.__name__
        counts = {m: m.query.count() for m in (User, Board, Card, Comment)}
        assert "already present" in runner.invoke(args=["seed-data"]).output
        assert counts == {m: m.query.count() for m in (User, Board, Card, Comment)}
        assert Comment.query.filter(Comment.parent_id.isnot(None)).count() == 2
        assert Board.query.filter_by(visibility="private").count() == 1


def test_seed_data_refuses_in_production(make_app):
    result = make_app("production").test_cli_runner().invoke(args=["seed-data"])
    assert result.exit_code != 0
