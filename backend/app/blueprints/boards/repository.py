from sqlalchemy.orm import selectinload

from app.extensions import db
from app.models import Board, BoardMember, Column, User


def get_by_id(board_id, include_deleted=False):
    board = db.session.get(Board, board_id)
    if board is None or (board.deleted_at is not None and not include_deleted):
        return None
    return board


def get_detail(board_id):
    """One board with its columns loaded (Req 3.10)."""
    board = db.session.scalars(
        db.select(Board)
        .where(Board.id == board_id, Board.deleted_at.is_(None))
        .options(selectinload(Board.columns))
        .execution_options(populate_existing=True)
    ).first()
    return board


def is_member(board_id, user_id):
    return BoardMember.query.filter_by(board_id=board_id, user_id=user_id).first() is not None


def list_visible(actor):
    q = Board.query.filter(Board.deleted_at.is_(None))
    if actor is None:
        q = q.filter(Board.visibility == "public")
    elif actor.role not in ("manager", "admin"):
        member_ids = db.select(BoardMember.board_id).where(BoardMember.user_id == actor.id)
        q = q.filter(db.or_(Board.visibility == "public", Board.owner_id == actor.id, Board.id.in_(member_ids)))
    return q.order_by(Board.created_at, Board.id).all()


def create_board(name, visibility, owner_id=None):
    board = Board(name=name, visibility=visibility, owner_id=owner_id)
    db.session.add(board)
    db.session.flush()
    return board


def add_column(board_id, name, order):
    col = Column(board_id=board_id, name=name, order=order)
    db.session.add(col)
    db.session.flush()
    return col


def max_column_order(board_id):
    return db.session.scalar(db.select(db.func.max(Column.order)).where(Column.board_id == board_id))


def list_columns(board_id):
    return Column.query.filter_by(board_id=board_id).order_by(Column.order).all()


def get_column(column_id):
    return db.session.get(Column, column_id)


def get_member(board_id, user_id):
    return BoardMember.query.filter_by(board_id=board_id, user_id=user_id).first()


def add_member(board_id, user_id):
    m = BoardMember(board_id=board_id, user_id=user_id)
    db.session.add(m)
    db.session.flush()
    return m


def delete_member(member):
    db.session.delete(member)


def list_members(board_id):
    return (
        User.query.join(BoardMember, BoardMember.user_id == User.id)
        .filter(BoardMember.board_id == board_id)
        .order_by(User.full_name)
        .all()
    )
