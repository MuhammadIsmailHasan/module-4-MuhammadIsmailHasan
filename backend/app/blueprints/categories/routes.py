from flask import Blueprint

from app.blueprints.categories import service
from app.common.auth import current_actor, require_role
from app.common.http import json_body
from app.common.responses import ok

bp = Blueprint("categories", __name__)
USERS = ("member", "supervisor", "manager", "admin")


@bp.get("/boards/<board_id>/categories")
def list_categories(board_id):
    return ok([service.serialize(c) for c in service.list_categories(current_actor(), board_id)])


@bp.post("/boards/<board_id>/categories")
@require_role(*USERS)
def create(board_id):
    return ok(service.serialize(service.create(current_actor(), board_id, json_body())), 201)


@bp.patch("/categories/<category_id>")
@require_role(*USERS)
def update(category_id):
    return ok(service.serialize(service.update(current_actor(), category_id, json_body())))


@bp.delete("/categories/<category_id>")
@require_role(*USERS)
def delete(category_id):
    service.delete(current_actor(), category_id)
    return ok(None)
