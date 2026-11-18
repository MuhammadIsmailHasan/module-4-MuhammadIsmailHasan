from flask import Blueprint

from app.blueprints.auth.schema import serialize_user_admin
from app.blueprints.users import service
from app.common.auth import current_actor, require_role
from app.common.http import json_body
from app.common.responses import ok

bp = Blueprint("users", __name__)


@bp.get("/users")
@require_role("admin")
def list_users():
    return ok([serialize_user_admin(u) for u in service.list_users()])


@bp.post("/users")
@require_role("admin")
def create_user():
    return ok(serialize_user_admin(service.create_user(current_actor(), json_body())), 201)


@bp.patch("/users/<user_id>")
@require_role("admin")
def update_user(user_id):
    return ok(serialize_user_admin(service.update_user(current_actor(), user_id, json_body())))
