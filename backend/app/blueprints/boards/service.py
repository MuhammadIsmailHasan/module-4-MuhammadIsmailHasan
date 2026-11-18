from app.blueprints.activity import repository as activity
from app.blueprints.auth import repository as users
from app.blueprints.boards import repository as repo
from app.blueprints.boards.dto import DEFAULT_COLUMNS, clean_name, clean_visibility
from app.common import clock
from app.common.errors import Forbidden, NotFound, Unauthorized, ValidationError
from app.common.ids import to_uuid
from app.extensions import db

PRIVILEGED = ("manager", "admin")


def is_owner(actor, board):
    return actor is not None and board.owner_id is not None and str(board.owner_id) == actor.id


def is_board_member(actor, board):
    return actor is not None and repo.is_member(board.id, to_uuid(actor.id))


def can_access(actor, board):
    if board is None or board.deleted_at is not None:
        return False
    if board.visibility == "public":
        return True
    if actor is None:
        return False
    return actor.role in PRIVILEGED or is_owner(actor, board) or is_board_member(actor, board)


def can_write_staff(actor, board):
    if actor is None or not can_access(actor, board):
        return False
    if actor.role in PRIVILEGED:
        return True
    return actor.role == "supervisor" and (is_owner(actor, board) or is_board_member(actor, board))


def require_access(actor, board):
    if board is None or board.deleted_at is not None:
        raise NotFound("Board not found")
    if not can_access(actor, board):
        if actor is None:
            raise Unauthorized("Authentication required")
        raise Forbidden("No access to this board")
    return board


def require_staff(actor, board):
    require_access(actor, board)
    if not can_write_staff(actor, board):
        raise Forbidden("Staff access required")


def load_board(actor, board_id):
    bid = to_uuid(board_id)
    board = repo.get_by_id(bid) if bid else None
    return require_access(actor, board)


def board_detail(actor, board_id):
    """Board with columns loaded; same 404/401/403 rules as load_board."""
    bid = to_uuid(board_id)
    board = repo.get_detail(bid) if bid else None
    return require_access(actor, board)


def reload_detail(board):
    return repo.get_detail(board.id)


def create_board(actor, data):
    name = clean_name(data.get("name"))
    visibility = clean_visibility(data.get("visibility", "private"))
    board = repo.create_board(name, visibility)
    for i, col_name in enumerate(DEFAULT_COLUMNS):
        repo.add_column(board.id, col_name, float(i))
    activity.add(to_uuid(actor.id), "board.created", "board", board.id, {"name": name})
    db.session.commit()
    return board


def update_board(actor, board_id, data):
    board = load_board(actor, board_id)
    meta = {}
    privileged = actor.role in PRIVILEGED
    if "owner_id" in data:
        if not privileged:
            raise Forbidden("Only Manager or Admin can change the owner")
        new_owner = data["owner_id"]
        if new_owner is None:
            board.owner_id = None
        else:
            uid = to_uuid(new_owner)
            user = users.get_by_id(uid) if uid else None
            if user is None or user.role != "supervisor":
                raise ValidationError("owner_id must reference a user with role supervisor")
            board.owner_id = user.id
        meta["owner_id"] = str(board.owner_id) if board.owner_id else None
        activity.add(to_uuid(actor.id), "board.owner_changed", "board", board.id, {"owner_id": meta["owner_id"]})
    if "visibility" in data:
        visibility = clean_visibility(data["visibility"])
        if not (privileged or (actor.role == "supervisor" and (is_owner(actor, board) or is_board_member(actor, board)))):
            raise Forbidden("Not allowed to change visibility")
        if visibility != board.visibility:
            board.visibility = visibility
            activity.add(to_uuid(actor.id), "board.visibility_changed", "board", board.id, {"visibility": visibility})
    if "name" in data:
        if not (privileged or is_owner(actor, board)):
            raise Forbidden("Not allowed to rename the board")
        board.name = clean_name(data["name"])
        activity.add(to_uuid(actor.id), "board.updated", "board", board.id, {"name": board.name})
    db.session.commit()
    return board


def _manager_only(actor, board_id, include_deleted=False):
    if actor.role not in PRIVILEGED:
        raise Forbidden("Manager or Admin only")
    bid = to_uuid(board_id)
    board = repo.get_by_id(bid) if bid else None
    if board is None:
        raise NotFound("Board not found")
    return board


def set_archived(actor, board_id, archived):
    board = _manager_only(actor, board_id)
    board.archived_at = clock.now() if archived else None
    activity.add(to_uuid(actor.id), "board.archived" if archived else "board.unarchived", "board", board.id)
    db.session.commit()
    return board


def soft_delete(actor, board_id):
    board = _manager_only(actor, board_id)
    board.deleted_at = clock.now()
    activity.add(to_uuid(actor.id), "board.deleted", "board", board.id)
    db.session.commit()


def list_boards(actor):
    return repo.list_visible(actor)


def require_manage_members(actor, board):
    if not (actor.role in PRIVILEGED or is_owner(actor, board)):
        raise Forbidden("Owner, Manager or Admin only")


def list_members(actor, board_id):
    board = load_board(actor, board_id)
    return repo.list_members(board.id)


def add_member(actor, board_id, data):
    board = load_board(actor, board_id)
    require_manage_members(actor, board)
    uid = to_uuid(data.get("user_id"))
    user = users.get_by_id(uid) if uid else None
    if user is None:
        raise NotFound("User not found")
    if repo.get_member(board.id, user.id):
        from app.common.errors import Conflict

        raise Conflict("User is already a member")
    repo.add_member(board.id, user.id)
    activity.add(to_uuid(actor.id), "board.member_added", "board", board.id, {"user_id": str(user.id)})
    db.session.commit()
    return user


def remove_member(actor, board_id, user_id):
    board = load_board(actor, board_id)
    require_manage_members(actor, board)
    uid = to_uuid(user_id)
    member = repo.get_member(board.id, uid) if uid else None
    if member is None:
        raise NotFound("Member not found")
    repo.delete_member(member)
    activity.add(to_uuid(actor.id), "board.member_removed", "board", board.id, {"user_id": str(uid)})
    db.session.commit()


def add_column(actor, board_id, data):
    board = load_board(actor, board_id)
    if not can_write_staff(actor, board):
        raise Forbidden("Staff access required")
    name = clean_name(data.get("name"))
    current = repo.max_column_order(board.id)
    col = repo.add_column(board.id, name, 0.0 if current is None else current + 1)
    activity.add(to_uuid(actor.id), "column.created", "column", col.id, {"board_id": str(board.id), "name": name})
    db.session.commit()
    return col
