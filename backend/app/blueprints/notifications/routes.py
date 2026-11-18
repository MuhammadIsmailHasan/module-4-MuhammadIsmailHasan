from flask import Blueprint

from app.blueprints.notifications import service
from app.common.auth import current_actor, require_role
from app.common.responses import ok

bp = Blueprint("notifications", __name__)
USERS = ("member", "supervisor", "manager", "admin")


@bp.get("/notifications")
@require_role(*USERS)
def inbox():
    return ok(service.inbox(current_actor()))


@bp.patch("/notifications/read-all")
@require_role(*USERS)
def read_all():
    service.mark_all_read(current_actor())
    return ok(None)


@bp.patch("/notifications/<notification_id>/read")
@require_role(*USERS)
def read_one(notification_id):
    return ok(service.serialize(service.mark_read(current_actor(), notification_id)))
