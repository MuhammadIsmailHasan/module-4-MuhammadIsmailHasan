from datetime import timedelta

from app.extensions import db
from app.models import Board, Card, Column


def summaries(today, week_ago, board_id=None):
    """One grouped query: per-board counts, no per-card data."""
    has_card = Card.id.isnot(None)  # the outer join yields NULL card rows for empty columns
    done = db.and_(has_card, Column.name == "Done")
    q = (
        db.select(
            Board.id,
            Board.name,
            db.func.count(Card.id),
            db.func.coalesce(db.func.sum(db.case((done, 1), else_=0)), 0),
            db.func.coalesce(db.func.sum(db.case((db.and_(has_card, Column.name == "In Progress"), 1), else_=0)), 0),
            db.func.coalesce(
                db.func.sum(db.case((db.and_(has_card, Card.end_date < today, Column.name != "Done"), 1), else_=0)), 0
            ),
            db.func.coalesce(db.func.sum(db.case((db.and_(done, Card.updated_at >= week_ago), 1), else_=0)), 0),
        )
        .select_from(Board)
        .outerjoin(Column, Column.board_id == Board.id)
        .outerjoin(Card, db.and_(Card.column_id == Column.id, Card.deleted_at.is_(None)))
        .where(Board.deleted_at.is_(None))
        .group_by(Board.id, Board.name)
        .order_by(Board.name, Board.id)
    )
    if board_id is not None:
        q = q.where(Board.id == board_id)
    return db.session.execute(q).all()
