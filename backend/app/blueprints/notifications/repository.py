from app.extensions import db
from app.models import Card, Notification


def _insert():
    if db.engine.dialect.name == "postgresql":
        from sqlalchemy.dialects.postgresql import insert
    else:
        from sqlalchemy.dialects.sqlite import insert
    return insert


def insert_ignore(user_id, card_id, type_, notify_date):
    """INSERT ... ON CONFLICT DO NOTHING on the unique (user, card, type, date)."""
    import uuid

    stmt = (
        _insert()(Notification)
        .values(id=uuid.uuid4(), user_id=user_id, card_id=card_id, type=type_, notify_date=notify_date, is_read=False)
        .on_conflict_do_nothing(index_elements=["user_id", "card_id", "type", "notify_date"])
    )
    db.session.execute(stmt)


def cards_due(today):
    return Card.query.filter(Card.end_date == today, Card.deleted_at.is_(None), Card.assignee_id.isnot(None)).all()


def list_for_user(user_id):
    return Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc(), Notification.id).all()


def get_for_user(notification_id, user_id):
    return Notification.query.filter_by(id=notification_id, user_id=user_id).first()


def mark_all_read(user_id):
    Notification.query.filter_by(user_id=user_id, is_read=False).update({"is_read": True})
