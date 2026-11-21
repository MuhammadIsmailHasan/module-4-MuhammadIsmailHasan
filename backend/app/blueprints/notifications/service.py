from app.blueprints.notifications import repository as repo
from app.common.errors import NotFound
from app.common.ids import to_uuid
from app.extensions import db


def _one(n, cards=None, boards=None, names=None):
    cards, boards, names = cards or {}, boards or {}, names or {}
    title, card_board = cards.get(n.card_id, (None, None))
    board_id = n.board_id or card_board
    return {
        "id": str(n.id),
        "type": n.type,
        "board_id": str(board_id) if board_id else None,
        "board_name": boards.get(board_id),
        "card_id": str(n.card_id) if n.card_id else None,
        "card_title": title,
        "actor_name": names.get(n.actor_id),
        "is_read": n.is_read,
        "notify_date": n.notify_date.isoformat(),
        "created_at": n.created_at.isoformat() if n.created_at else None,
    }


def serialize_many(rows):
    """Names are loaded in three queries whatever the number of rows (Requirement 28, criterion 4)."""
    cards = repo.card_context({n.card_id for n in rows if n.card_id})
    board_ids = {n.board_id for n in rows if n.board_id} | {b for _, b in cards.values()}
    boards = repo.board_names(board_ids)
    names = repo.user_names({n.actor_id for n in rows if n.actor_id})
    return [_one(n, cards, boards, names) for n in rows]


def serialize(n):
    return serialize_many([n])[0]


def inbox(actor, limit=None, before=None):
    uid = to_uuid(actor.id)
    rows = repo.list_for_user(uid, limit, before)
    return {"items": serialize_many(rows), "unread_count": repo.unread_count(uid)}


def mark_read(actor, notification_id):
    nid = to_uuid(notification_id)
    n = repo.get_for_user(nid, to_uuid(actor.id)) if nid else None
    if n is None:
        raise NotFound("Notification not found")
    n.is_read = True
    db.session.commit()
    return n


def mark_all_read(actor):
    repo.mark_all_read(to_uuid(actor.id))
    db.session.commit()
