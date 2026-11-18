from flask import Blueprint

from app.blueprints.analytics import service
from app.common.auth import current_actor, require_role
from app.common.responses import ok

bp = Blueprint("analytics", __name__)


@bp.get("/boards/<board_id>/analytics")
@require_role("member", "supervisor", "manager", "admin")
def board_analytics(board_id):
    return ok(service.board_analytics(current_actor(), board_id))


@bp.get("/analytics/boards")
@require_role("manager")
def all_boards():
    return ok(service.all_boards(current_actor()))
