import uuid
from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Attachment, Board, Card, Category, Column, Notification, User


def _add(obj):
    db.session.add(obj)
    db.session.commit()
    return obj


@pytest.fixture
def base(make_user):
    u = make_user("member")
    b = _add(Board(name="b"))
    c = _add(Column(board_id=b.id, name="c", order=0))
    return u, b, c


def test_username_and_email_case_insensitive_unique(app):
    _add(User(full_name="a", username="Ann", email="A@x.com", password_hash="h"))
    with pytest.raises(IntegrityError):
        _add(User(full_name="b", username="ANN", email="b@x.com", password_hash="h"))
    db.session.rollback()
    with pytest.raises(IntegrityError):
        _add(User(full_name="c", username="cat", email="a@X.com", password_hash="h"))
    db.session.rollback()


def test_category_name_unique_per_board_case_insensitive(base):
    _, b, _ = base
    _add(Category(board_id=b.id, name="Bug"))
    with pytest.raises(IntegrityError):
        _add(Category(board_id=b.id, name="bUG"))
    db.session.rollback()
    other = _add(Board(name="o"))
    _add(Category(board_id=other.id, name="bug"))


def test_card_date_check_and_attachment_check_and_notification_unique(base):
    u, b, c = base
    with pytest.raises(IntegrityError):
        _add(Card(column_id=c.id, title="t", order=1, start_date=date(2026, 2, 2), end_date=date(2026, 2, 1)))
    db.session.rollback()
    card = _add(Card(column_id=c.id, title="t", order=1))
    with pytest.raises(IntegrityError):
        _add(Attachment(card_id=card.id, name="n"))
    db.session.rollback()
    kw = dict(user_id=u.id, card_id=card.id, type="deadline", notify_date=date(2026, 1, 1))
    _add(Notification(**kw))
    with pytest.raises(IntegrityError):
        _add(Notification(**kw))
    db.session.rollback()
