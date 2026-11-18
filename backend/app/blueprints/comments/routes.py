from flask import Blueprint, request

from app.blueprints.comments import service
from app.common.auth import current_actor, require_role
from app.common.http import json_body
from app.common.responses import ok

bp = Blueprint("comments", __name__)


@bp.post("/cards/<card_id>/comments")
def create(card_id):
    c = service.create_comment(current_actor(), card_id, json_body())
    return ok(service.serialize(c, current_actor().role, {}), 201)


@bp.post("/comments/<comment_id>/replies")
def reply(comment_id):
    c = service.reply(current_actor(), comment_id, json_body())
    return ok(service.serialize(c, current_actor().role, {}), 201)


@bp.patch("/comments/<comment_id>/priority")
@require_role("manager")
def priority(comment_id):
    c = service.toggle_priority(current_actor(), comment_id)
    return ok(service.serialize(c, "manager", {}))


@bp.get("/cards/<card_id>/comments")
def list_comments(card_id):
    return ok(service.list_for_request(current_actor(), card_id, request.args.get("sort")))
