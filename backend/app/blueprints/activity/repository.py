"""Append-only: `add` is the only write function."""
from app.common import clock
from app.extensions import db
from app.models import ActivityLog, Card, Column


def add(actor_id, action, target_type, target_id, metadata=None):
    row = ActivityLog(
        actor_id=actor_id, action=action, target_type=target_type, target_id=target_id, metadata_=metadata,
        created_at=clock.now(),
    )
    db.session.add(row)
    return row


def for_card(card_id):
    return (
        ActivityLog.query.filter_by(target_type="card", target_id=card_id)
        .order_by(ActivityLog.created_at.desc(), ActivityLog.id)
        .all()
    )


def for_board(board_id):
    column_ids = db.select(Column.id).where(Column.board_id == board_id)
    card_ids = db.select(Card.id).join(Column, Card.column_id == Column.id).where(Column.board_id == board_id)
    cond = db.or_(
        db.and_(ActivityLog.target_type == "board", ActivityLog.target_id == board_id),
        db.and_(ActivityLog.target_type == "column", ActivityLog.target_id.in_(column_ids)),
        db.and_(ActivityLog.target_type == "card", ActivityLog.target_id.in_(card_ids)),
    )
    return ActivityLog.query.filter(cond).order_by(ActivityLog.created_at.desc(), ActivityLog.id).all()


def serialize(row):
    return {
        "id": str(row.id),
        "actor_id": str(row.actor_id),
        "action": row.action,
        "target_type": row.target_type,
        "target_id": str(row.target_id),
        "metadata": row.metadata_,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }
