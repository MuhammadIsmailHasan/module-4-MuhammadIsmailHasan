from app.common import clock
from app.extensions import db
from app.models import Card, Comment, User


def get(comment_id):
    c = db.session.get(Comment, comment_id)
    if c is None:
        return None
    card = db.session.get(Card, c.card_id)
    return c if card is not None and card.deleted_at is None else None


def add(card_id, author_id, content, parent_id=None):
    c = Comment(card_id=card_id, author_id=author_id, content=content, parent_id=parent_id,
                created_at=clock.now())
    db.session.add(c)
    db.session.flush()
    return c


def for_card(card_id):
    return Comment.query.filter_by(card_id=card_id).all()


def author_roles(ids):
    if not ids:
        return {}
    return {u.id: u.role for u in User.query.filter(User.id.in_(ids)).all()}
