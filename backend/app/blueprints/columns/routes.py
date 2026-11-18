from flask import Blueprint

from app.blueprints.boards import service
from app.blueprints.boards.schema import serialize_column
from app.common.auth import current_actor, require_role
from app.common.http import json_body
from app.common.responses import ok

bp = Blueprint("columns", __name__)


@bp.post("/boards/<board_id>/columns")
@require_role("member", "supervisor", "manager", "admin")
def create_column(board_id):
    return ok(serialize_column(service.add_column(current_actor(), board_id, json_body())), 201)
