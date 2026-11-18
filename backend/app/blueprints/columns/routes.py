from flask_smorest import Blueprint

from app.blueprints.boards import service
from app.blueprints.boards.dto import serialize_column
from app.blueprints.boards.schema import ColumnSchema, CreateColumnSchema
from app.common.auth import current_actor, require_role
from app.common.docs import endpoint
from app.common.envelope import envelope
from app.common.responses import ok

bp = Blueprint("columns", __name__, description="Board columns")


@bp.route("/boards/<board_id>/columns", methods=["POST"])
@endpoint(bp, "Add a column", "Staff access on the board. Appended with order = max + 1.", errors=(400, 401, 403, 404))
@require_role("member", "supervisor", "manager", "admin")
@bp.arguments(CreateColumnSchema)
@bp.response(201, envelope(ColumnSchema))
def create_column(data, board_id):
    return ok(serialize_column(service.add_column(current_actor(), board_id, data)), "Column created", 201)
