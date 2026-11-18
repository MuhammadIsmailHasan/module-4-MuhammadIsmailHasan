from app.blueprints.activity import repository as activity
from app.blueprints.boards import repository as boards_repo
from app.blueprints.boards import service as boards
from app.blueprints.cards import repository as cards_repo
from app.blueprints.comments import repository as repo
from app.common.errors import Forbidden, NotFound, ValidationError
from app.common.ids import to_uuid
from app.extensions import db

WRITERS = ("member", "supervisor", "manager")
STAFF = ("supervisor", "manager", "admin")


def _load_card(actor, card_id):
    cid = to_uuid(card_id)
    card = cards_repo.get_card(cid) if cid else None
    if card is None:
        raise NotFound("Card not found")
    board = boards_repo.get_by_id(cards_repo.board_id_of_card(card))
    boards.require_access(actor, board)
    return card


def _require_commenter(actor):
    # Guest: 403 on public boards (401 on private comes from require_access).
    if actor is None or actor.role not in WRITERS:
        raise Forbidden("Comments are not available for this role")


def _content(data):
    content = data.get("content")
    if not isinstance(content, str) or not content.strip():
        raise ValidationError("content is required")
    return content.strip()


def create_comment(actor, card_id, data):
    card = _load_card(actor, card_id)
    _require_commenter(actor)
    c = repo.add(card.id, to_uuid(actor.id), _content(data))
    activity.add(to_uuid(actor.id), "comment.added", "card", card.id, {"comment_id": str(c.id)})
    db.session.commit()
    return c


def reply(actor, comment_id, data):
    cid = to_uuid(comment_id)
    parent = repo.get(cid) if cid else None
    if parent is None:
        raise NotFound("Comment not found")
    card = _load_card(actor, parent.card_id)
    _require_commenter(actor)
    if parent.parent_id is not None:
        raise ValidationError("Replies cannot be nested more than one level")
    c = repo.add(card.id, to_uuid(actor.id), _content(data), parent_id=parent.id)
    parent.reply_count = (parent.reply_count or 0) + 1
    activity.add(to_uuid(actor.id), "comment.replied", "card", card.id, {"comment_id": str(c.id)})
    db.session.commit()
    return c


def toggle_priority(actor, comment_id):
    cid = to_uuid(comment_id)
    c = repo.get(cid) if cid else None
    if c is None:
        raise NotFound("Comment not found")
    _load_card(actor, c.card_id)
    c.is_priority = not c.is_priority
    activity.add(to_uuid(actor.id), "comment.priority_toggled", "card", c.card_id, {"is_priority": c.is_priority})
    db.session.commit()
    return c


def serialize(c, viewer_role, author_roles, replies=None):
    data = {
        "id": str(c.id),
        "card_id": str(c.card_id),
        "author_id": str(c.author_id),
        "parent_id": str(c.parent_id) if c.parent_id else None,
        "content": c.content,
        "is_priority": c.is_priority,
        "reply_count": c.reply_count,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "can_create_card": viewer_role in STAFF and author_roles.get(c.author_id) == "manager",
    }
    if replies is not None:
        data["replies"] = replies
    return data


def list_comments(card, actor, sort="latest"):
    if sort not in ("latest", "popular"):
        raise ValidationError("sort must be latest or popular")
    rows = repo.for_card(card.id)
    roles = repo.author_roles({r.author_id for r in rows})
    top = [r for r in rows if r.parent_id is None]
    key_time = lambda r: (r.created_at, str(r.id))  # noqa: E731
    priority = sorted((r for r in top if r.is_priority), key=key_time, reverse=True)
    others = [r for r in top if not r.is_priority]
    if sort == "popular":
        others.sort(key=lambda r: (r.reply_count, r.created_at, str(r.id)), reverse=True)
    else:
        others.sort(key=key_time, reverse=True)
    replies = {}
    for r in sorted((r for r in rows if r.parent_id is not None), key=lambda r: (r.created_at, str(r.id))):
        replies.setdefault(r.parent_id, []).append(r)
    return [
        serialize(c, actor.role, roles, [serialize(x, actor.role, roles) for x in replies.get(c.id, [])])
        for c in priority + others
    ]


def list_for_request(actor, card_id, sort):
    card = _load_card(actor, card_id)
    if actor is None:
        raise Forbidden("Comments are not available to guests")
    return list_comments(card, actor, sort or "latest")
