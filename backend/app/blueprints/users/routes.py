from flask_smorest import Blueprint

from app.blueprints.auth.dto import serialize_user_admin
from app.blueprints.auth.schema import AdminUserSchema
from app.blueprints.users import service
from app.blueprints.users.schema import CreateUserSchema, UpdateUserSchema
from app.common.auth import current_actor, require_role
from app.common.docs import endpoint
from app.common.envelope import envelope
from app.common.responses import ok

bp = Blueprint("users", __name__, description="User administration (Admin only)")


@bp.route("/users", methods=["GET"])
@endpoint(bp, "List users", "Admin only.", errors=(401, 403))
@require_role("admin")
@bp.response(200, envelope(AdminUserSchema, many=True))
def list_users():
    return ok([serialize_user_admin(u) for u in service.list_users()])


@bp.route("/users", methods=["POST"])
@endpoint(bp, "Create a user", "Admin only. Logs user.created.", errors=(400, 401, 403, 409))
@require_role("admin")
@bp.arguments(CreateUserSchema)
@bp.response(201, envelope(AdminUserSchema))
def create_user(data):
    return ok(serialize_user_admin(service.create_user(current_actor(), data)), "User created", 201)


@bp.route("/users/<user_id>", methods=["PATCH"])
@endpoint(bp, "Update a user or assign a role", "Admin only. Logs user.updated and user.role_changed.", errors=(400, 401, 403, 404, 409))
@require_role("admin")
@bp.arguments(UpdateUserSchema)
@bp.response(200, envelope(AdminUserSchema))
def update_user(data, user_id):
    return ok(serialize_user_admin(service.update_user(current_actor(), user_id, data)), "User updated")
