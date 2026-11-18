from marshmallow import fields

from app.common.fields import BaseSchema


class NotificationSchema(BaseSchema):
    id = fields.UUID()
    type = fields.String(metadata={"description": "assigned or deadline"})
    card_id = fields.UUID()
    is_read = fields.Boolean()
    notify_date = fields.String()
    created_at = fields.String(allow_none=True)


class InboxSchema(BaseSchema):
    items = fields.List(fields.Nested(NotificationSchema))
    unread_count = fields.Integer()
