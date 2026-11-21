from flask import request
from flask_smorest import Blueprint

from app.blueprints.invites import service
from app.blueprints.invites.schema import (
    DecideSchema,
    InviteSchema,
    InviteStateSchema,
    JoinRequestListQuerySchema,
    JoinRequestRowSchema,
    JoinRequestSchema,
)
from app.common.auth import current_actor, require_role
from app.common.docs import endpoint
from app.common.envelope import envelope
from app.common.responses import ok

USERS = ("member", "supervisor", "manager", "admin")
bp = Blueprint("invites", __name__, description="Invite link and join requests")
_MANAGE = (401, 403, 404)


@bp.after_request
def _no_store(response):
    if request.path.startswith("/api/invite"):
        response.headers["Cache-Control"] = "private, no-store"
    return response


@bp.route("/boards/<board_id>/invite", methods=["GET"])
@endpoint(bp, "Get the invite link state", "Board owner, Manager or Admin only.", errors=_MANAGE)
@require_role(*USERS)
@bp.response(200, envelope(InviteSchema))
def get_invite(board_id):
    return ok(service.get_invite(current_actor(), board_id))


@bp.route("/boards/<board_id>/invite", methods=["POST"])
@endpoint(bp, "Enable the invite link", "Creates a 256-bit token when invites are off; returns the existing one otherwise.", errors=_MANAGE)
@require_role(*USERS)
@bp.response(200, envelope(InviteSchema))
def enable_invite(board_id):
    return ok(service.enable(current_actor(), board_id), "Invite link enabled")


@bp.route("/boards/<board_id>/invite/regenerate", methods=["POST"])
@endpoint(bp, "Replace the invite token", "The previous link stops working at once. Pending requests stay pending.", errors=_MANAGE)
@require_role(*USERS)
@bp.response(200, envelope(InviteSchema))
def regenerate_invite(board_id):
    return ok(service.regenerate(current_actor(), board_id), "Invite link replaced")


@bp.route("/boards/<board_id>/invite", methods=["DELETE"])
@endpoint(bp, "Disable the invite link", "Idempotent: 200 when invites are already off.", errors=_MANAGE)
@require_role(*USERS)
@bp.response(200, envelope(InviteSchema))
def disable_invite(board_id):
    return ok(service.disable(current_actor(), board_id), "Invite link disabled")


@bp.route("/invite/<token>", methods=["GET"])
@endpoint(bp, "Look up an invite", "Signed-in users only. One 404 for an unknown, disabled, replaced or deleted-board token.", errors=(401, 404))
@require_role(*USERS)
@bp.response(200, envelope(InviteStateSchema))
def get_state(token):
    return ok(service.resolve(current_actor(), token))


@bp.route("/invite/<token>/requests", methods=["POST"])
@endpoint(bp, "Ask to join a board", "Member or Supervisor who is not on the board. 400 for Manager and Admin, 409 when already in or pending.", errors=(400, 401, 404, 409))
@require_role(*USERS)
@bp.response(201, envelope(JoinRequestSchema))
def create_request(token):
    return ok(service.create_request(current_actor(), token), "Request sent", 201)


@bp.route("/boards/<board_id>/join-requests", methods=["GET"])
@endpoint(bp, "List join requests", "Board owner, Manager or Admin. Each user carries the Email. `?status=pending|approved|rejected|all`.", errors=_MANAGE)
@require_role(*USERS)
@bp.arguments(JoinRequestListQuerySchema, location="query")
@bp.response(200, envelope(JoinRequestRowSchema, many=True))
def list_requests(args, board_id):
    return ok(service.list_requests(current_actor(), board_id, args["status"]))


@bp.route("/join-requests/<request_id>", methods=["PATCH"])
@endpoint(bp, "Approve or reject a join request", "Manager or Admin only. 409 when already decided.", errors=(400, 401, 403, 404, 409))
@require_role("manager", "admin")
@bp.arguments(DecideSchema)
@bp.response(200, envelope(JoinRequestSchema))
def decide(data, request_id):
    return ok(service.decide(current_actor(), request_id, data["status"]), "Request decided")
