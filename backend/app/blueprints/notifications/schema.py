from marshmallow import fields

from app.common.fields import BaseSchema


class NotificationSchema(BaseSchema):
    id = fields.UUID()
    type = fields.String(metadata={"description": "assigned, deadline, board_join_requested, board_added or board_join_rejected"})
    board_id = fields.UUID(allow_none=True)
    board_name = fields.String(allow_none=True)
    card_id = fields.UUID(allow_none=True)
    card_title = fields.String(allow_none=True)
    actor_name = fields.String(allow_none=True)
    is_read = fields.Boolean()
    notify_date = fields.String()
    created_at = fields.String(allow_none=True)


class InboxSchema(BaseSchema):
    items = fields.List(fields.Nested(NotificationSchema))
    unread_count = fields.Integer()
