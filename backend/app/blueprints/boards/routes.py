from flask_smorest import Blueprint

from app.blueprints.activity import repository as activity
from app.blueprints.activity.schema import ActivitySchema
from app.blueprints.auth.dto import serialize_user
from app.blueprints.auth.schema import UserSchema
from app.blueprints.boards import repository as repo
from app.blueprints.boards import service
from app.blueprints.boards.dto import serialize_board
from app.blueprints.boards.schema import (
    AddMemberSchema,
    BoardSchema,
    CreateBoardSchema,
    UpdateBoardSchema,
)
from app.common.auth import current_actor, require_role
from app.common.docs import endpoint
from app.common.envelope import NullEnvelopeSchema, envelope
from app.common.errors import Forbidden
from app.common.responses import ok

bp = Blueprint("boards", __name__, description="Boards, visibility, archive and members")
ANY_USER = ("member", "supervisor", "manager", "admin")


@bp.route("/boards", methods=["POST"])
@endpoint(bp, "Create a board", "Manager or Admin. Seeds Todo, In Progress, Review, Revision, Done.", errors=(400, 401, 403))
@require_role("manager", "admin")
@bp.arguments(CreateBoardSchema)
@bp.response(201, envelope(BoardSchema))
def create_board(data):
    board = service.create_board(current_actor(), data)
    return ok(serialize_board(board, repo.list_columns(board.id)), "Board created", 201)


@bp.route("/boards", methods=["GET"])
@endpoint(bp, "List visible boards", "Guests see public boards; signed-in users see public plus accessible boards.", auth="optional", errors=())
@bp.response(200, envelope(BoardSchema, many=True))
def list_boards():
    return ok([serialize_board(b) for b in service.list_boards(current_actor())], "Boards retrieved")


@bp.route("/boards/<board_id>", methods=["GET"])
@endpoint(bp, "Get a board with its columns", "Guests may read public boards. Private boards: 401 for Guests, 403 without access.", auth="optional")
@bp.response(200, envelope(BoardSchema))
def get_board(board_id):
    board = service.load_board(current_actor(), board_id)
    return ok(serialize_board(board, repo.list_columns(board.id), current_actor()), "Board retrieved")


@bp.route("/boards/<board_id>", methods=["PATCH"])
@endpoint(bp, "Update name, visibility or owner", "owner_id: Manager or Admin, new owner must be a supervisor. visibility: Manager, Admin, owner or member Supervisor. name: Manager, Admin or owner.", errors=(400, 401, 403, 404))
@require_role(*ANY_USER)
@bp.arguments(UpdateBoardSchema)
@bp.response(200, envelope(BoardSchema))
def update_board(data, board_id):
    board = service.update_board(current_actor(), board_id, data)
    return ok(serialize_board(board, repo.list_columns(board.id)), "Board updated")


@bp.route("/boards/<board_id>/archive", methods=["POST"])
@endpoint(bp, "Archive a board", "Manager or Admin.", errors=(401, 403, 404))
@require_role("manager", "admin")
@bp.response(200, envelope(BoardSchema))
def archive(board_id):
    return ok(serialize_board(service.set_archived(current_actor(), board_id, True)), "Board archived")


@bp.route("/boards/<board_id>/unarchive", methods=["POST"])
@endpoint(bp, "Unarchive a board", "Manager or Admin.", errors=(401, 403, 404))
@require_role("manager", "admin")
@bp.response(200, envelope(BoardSchema))
def unarchive(board_id):
    return ok(serialize_board(service.set_archived(current_actor(), board_id, False)), "Board unarchived")


@bp.route("/boards/<board_id>", methods=["DELETE"])
@endpoint(bp, "Soft-delete a board", "Manager or Admin. Sets deleted_at; nothing is removed.", errors=(401, 403, 404))
@require_role("manager", "admin")
@bp.response(200, NullEnvelopeSchema)
def delete_board(board_id):
    service.soft_delete(current_actor(), board_id)
    return ok(None, "Board deleted")


@bp.route("/boards/<board_id>/members", methods=["GET"])
@endpoint(bp, "List board members", "Requires board access.", auth="optional")
@bp.response(200, envelope(UserSchema, many=True))
def members(board_id):
    return ok([serialize_user(u) for u in service.list_members(current_actor(), board_id)], "Members retrieved")


@bp.route("/boards/<board_id>/members", methods=["POST"])
@endpoint(bp, "Add a board member", "Owner, Manager or Admin. 409 when already a member.", errors=(400, 401, 403, 404, 409))
@require_role(*ANY_USER)
@bp.arguments(AddMemberSchema)
@bp.response(201, envelope(UserSchema))
def add_member(data, board_id):
    return ok(serialize_user(service.add_member(current_actor(), board_id, data)), "Member added", 201)


@bp.route("/boards/<board_id>/members/<user_id>", methods=["DELETE"])
@endpoint(bp, "Remove a board member", "Owner, Manager or Admin.", errors=(401, 403, 404))
@require_role(*ANY_USER)
@bp.response(200, NullEnvelopeSchema)
def remove_member(board_id, user_id):
    service.remove_member(current_actor(), board_id, user_id)
    return ok(None, "Member removed")


@bp.route("/boards/<board_id>/activity", methods=["GET"])
@endpoint(bp, "Board activity feed", "Requires board access; Guests get 403 (never activity).", auth="optional")
@bp.response(200, envelope(ActivitySchema, many=True))
def board_activity(board_id):
    actor = current_actor()
    board = service.load_board(actor, board_id)
    if actor is None:
        raise Forbidden("Activity is not available to guests")
    return ok([activity.serialize(r) for r in activity.for_board(board.id)], "Activity retrieved")
