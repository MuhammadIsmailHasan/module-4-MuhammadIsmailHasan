from app.extensions import db
from app.models import Attachment, Board, Card, Category, Column, Subtask


def get_card(card_id, include_deleted=False):
    card = db.session.get(Card, card_id)
    if card is None or (card.deleted_at is not None and not include_deleted):
        return None
    return card


def get_column(column_id):
    return db.session.get(Column, column_id)


def board_id_of_card(card):
    return db.session.scalar(db.select(Column.board_id).where(Column.id == card.column_id))


def max_order(column_id):
    return db.session.scalar(
        db.select(db.func.max(Card.order)).where(Card.column_id == column_id, Card.deleted_at.is_(None))
    )


def column_cards(column_id, exclude_id=None):
    q = Card.query.filter(Card.column_id == column_id, Card.deleted_at.is_(None))
    if exclude_id is not None:
        q = q.filter(Card.id != exclude_id)
    return q.order_by(Card.order).all()


def add_card(**fields):
    card = Card(**fields)
    db.session.add(card)
    db.session.flush()
    return card


def get_category(category_id):
    return db.session.get(Category, category_id)


def subtasks_of(card_id):
    return Subtask.query.filter_by(card_id=card_id).order_by(Subtask.order).all()


def max_subtask_order(card_id):
    return db.session.scalar(db.select(db.func.max(Subtask.order)).where(Subtask.card_id == card_id))


def add_subtask(card_id, title, order):
    s = Subtask(card_id=card_id, title=title, order=order, is_done=False)
    db.session.add(s)
    db.session.flush()
    return s


def get_subtask(subtask_id):
    sub = db.session.get(Subtask, subtask_id)
    if sub is None:
        return None
    card = db.session.get(Card, sub.card_id)
    return sub if card is not None and card.deleted_at is None else None


def delete_subtask(sub):
    db.session.delete(sub)


def attachments_of(card_id):
    return Attachment.query.filter_by(card_id=card_id).order_by(Attachment.created_at, Attachment.id).all()


def add_attachment(**fields):
    a = Attachment(**fields)
    db.session.add(a)
    db.session.flush()
    return a


def get_attachment(attachment_id):
    return db.session.get(Attachment, attachment_id)


def delete_attachment(att):
    db.session.delete(att)


def search_cards(board_id, search=None, priority=None, assignee=None, category=None):
    q = (
        Card.query.join(Column, Card.column_id == Column.id)
        .join(Board, Board.id == Column.board_id)
        .filter(Column.board_id == board_id, Card.deleted_at.is_(None))
    )
    if search:
        like = f"%{search.lower()}%"
        q = q.filter(db.or_(db.func.lower(Card.title).like(like), db.func.lower(Card.description).like(like)))
    if priority:
        q = q.filter(Card.priority == priority)
    if assignee:
        q = q.filter(Card.assignee_id == assignee)
    if category:
        q = q.filter(Card.category_id == category)
    return q.order_by(Column.order, Card.order).all()
