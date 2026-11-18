from flask import Blueprint

from app.blueprints.activity import repository as activity
from app.blueprints.auth.schema import serialize_user
from app.blueprints.boards import repository as repo
from app.blueprints.boards import service
from app.blueprints.boards.schema import serialize_board, serialize_column
from app.common.auth import current_actor, require_role
from app.common.errors import Forbidden
from app.common.http import json_body
from app.common.responses import ok

bp = Blueprint("boards", __name__)
ANY_USER = ("member", "supervisor", "manager", "admin")


@bp.post("/boards")
@require_role("manager", "admin")
def create_board():
    board = service.create_board(current_actor(), json_body())
    return ok(serialize_board(board, repo.list_columns(board.id)), 201)


@bp.get("/boards")
def list_boards():
    return ok([serialize_board(b) for b in service.list_boards(current_actor())])


@bp.get("/boards/<board_id>")
def get_board(board_id):
    board = service.load_board(current_actor(), board_id)
    return ok(serialize_board(board, repo.list_columns(board.id), current_actor()))


@bp.patch("/boards/<board_id>")
@require_role(*ANY_USER)
def update_board(board_id):
    board = service.update_board(current_actor(), board_id, json_body())
    return ok(serialize_board(board, repo.list_columns(board.id)))


@bp.post("/boards/<board_id>/archive")
@require_role("manager", "admin")
def archive(board_id):
    return ok(serialize_board(service.set_archived(current_actor(), board_id, True)))


@bp.post("/boards/<board_id>/unarchive")
@require_role("manager", "admin")
def unarchive(board_id):
    return ok(serialize_board(service.set_archived(current_actor(), board_id, False)))


@bp.delete("/boards/<board_id>")
@require_role("manager", "admin")
def delete_board(board_id):
    service.soft_delete(current_actor(), board_id)
    return ok(None)


@bp.get("/boards/<board_id>/members")
def members(board_id):
    return ok([serialize_user(u) for u in service.list_members(current_actor(), board_id)])


@bp.post("/boards/<board_id>/members")
@require_role(*ANY_USER)
def add_member(board_id):
    return ok(serialize_user(service.add_member(current_actor(), board_id, json_body())), 201)


@bp.delete("/boards/<board_id>/members/<user_id>")
@require_role(*ANY_USER)
def remove_member(board_id, user_id):
    service.remove_member(current_actor(), board_id, user_id)
    return ok(None)


@bp.get("/boards/<board_id>/activity")
def board_activity(board_id):
    actor = current_actor()
    board = service.load_board(actor, board_id)
    if actor is None:
        raise Forbidden("Activity is not available to guests")
    return ok([activity.serialize(r) for r in activity.for_board(board.id)])
