from flask_smorest import Blueprint

from app.blueprints.notifications import service
from app.blueprints.notifications.schema import InboxSchema, NotificationSchema
from app.common.auth import current_actor, require_role
from app.common.docs import endpoint
from app.common.envelope import NullEnvelopeSchema, envelope
from app.common.responses import ok

bp = Blueprint("notifications", __name__, description="Inbox (created server-side only)")
USERS = ("member", "supervisor", "manager", "admin")


@bp.route("/notifications", methods=["GET"])
@endpoint(bp, "List my notifications", "Only the caller's rows.", errors=(401,))
@require_role(*USERS)
@bp.response(200, envelope(InboxSchema))
def inbox():
    return ok(service.inbox(current_actor()), "Notifications retrieved")


@bp.route("/notifications/read-all", methods=["PATCH"])
@endpoint(bp, "Mark all my notifications read", errors=(401,))
@require_role(*USERS)
@bp.response(200, NullEnvelopeSchema)
def read_all():
    service.mark_all_read(current_actor())
    return ok(None, "All notifications marked read")


@bp.route("/notifications/<notification_id>/read", methods=["PATCH"])
@endpoint(bp, "Mark one notification read", "404 for another user's or unknown id.", errors=(401, 404))
@require_role(*USERS)
@bp.response(200, envelope(NotificationSchema))
def read_one(notification_id):
    return ok(service.serialize(service.mark_read(current_actor(), notification_id)), "Notification marked read")
