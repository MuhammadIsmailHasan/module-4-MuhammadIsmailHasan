from marshmallow import fields

from app.common.fields import BaseSchema


class ActivitySchema(BaseSchema):
    id = fields.UUID()
    actor_id = fields.UUID()
    action = fields.String(metadata={"description": "For example card.moved, board.member_added"})
    target_type = fields.String(metadata={"description": "card, board, column or user"})
    target_id = fields.UUID()
    meta_data = fields.Raw(attribute="metadata", data_key="metadata", allow_none=True)
    created_at = fields.String()
