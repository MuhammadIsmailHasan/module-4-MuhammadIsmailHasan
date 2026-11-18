from app.blueprints.activity import repository as activity
from app.blueprints.boards import repository as boards_repo
from app.blueprints.boards import service as boards
from app.blueprints.categories import repository as repo
from app.common.errors import Conflict, NotFound, ValidationError
from app.common.ids import to_uuid
from app.extensions import db


def serialize(c):
    return {"id": str(c.id), "board_id": str(c.board_id), "name": c.name, "color": c.color}


def _name(value):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError("name is required")
    value = value.strip()
    if len(value) > 255:
        raise ValidationError("name must be at most 255 characters")
    return value


def list_categories(actor, board_id):
    board = boards.load_board(actor, board_id)
    return repo.list_for_board(board.id)


def create(actor, board_id, data):
    board = boards.load_board(actor, board_id)
    boards.require_staff(actor, board)
    name = _name(data.get("name"))
    if repo.find_by_name(board.id, name):
        raise Conflict("A category with this name already exists")
    cat = repo.add(board.id, name, data.get("color"))
    db.session.commit()
    return cat


def _load(actor, category_id):
    cid = to_uuid(category_id)
    cat = repo.get(cid) if cid else None
    if cat is None:
        raise NotFound("Category not found")
    board = boards_repo.get_by_id(cat.board_id)
    boards.require_staff(actor, board)
    return cat


def update(actor, category_id, data):
    cat = _load(actor, category_id)
    if "name" in data:
        name = _name(data["name"])
        if repo.find_by_name(cat.board_id, name, exclude_id=cat.id):
            raise Conflict("A category with this name already exists")
        cat.name = name
    if "color" in data:
        cat.color = data["color"]
    db.session.commit()
    return cat


def delete(actor, category_id):
    cat = _load(actor, category_id)
    repo.delete(cat)
    db.session.commit()
