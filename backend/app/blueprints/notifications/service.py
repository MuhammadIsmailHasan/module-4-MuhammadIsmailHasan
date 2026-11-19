from app.blueprints.notifications import repository as repo
from app.common.errors import NotFound
from app.common.ids import to_uuid
from app.extensions import db


def serialize(n):
    return {
        "id": str(n.id),
        "type": n.type,
        "card_id": str(n.card_id),
        "is_read": n.is_read,
        "notify_date": n.notify_date.isoformat(),
        "created_at": n.created_at.isoformat() if n.created_at else None,
    }


def inbox(actor, limit=None, before=None):
    uid = to_uuid(actor.id)
    rows = repo.list_for_user(uid, limit, before)
    return {"items": [serialize(n) for n in rows], "unread_count": repo.unread_count(uid)}


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
