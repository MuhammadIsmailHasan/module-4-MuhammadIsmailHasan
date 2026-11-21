from marshmallow import fields, validate

from app.blueprints.activity.schema import ActivitySchema
from app.blueprints.comments.schema import CommentSchema
from app.common.fields import BaseSchema, Text

_priority = validate.OneOf(["high", "medium", "low"], error="priority must be high, medium or low")


class _CardFields(BaseSchema):
    description = fields.String(allow_none=True)
    priority = fields.String(validate=_priority)
    start_date = fields.Date(allow_none=True)
    end_date = fields.Date(allow_none=True, metadata={"description": "Must be on or after start_date"})
    category_id = fields.UUID(allow_none=True, metadata={"description": "Category of the same board"})
    assignee_id = fields.UUID(allow_none=True)


class CreateCardSchema(_CardFields):
    title = Text(required=True, max_length=255)


class UpdateCardSchema(_CardFields):
    title = Text(max_length=255)


class MoveCardSchema(BaseSchema):
    column_id = fields.UUID(required=True)
    prev = fields.UUID(allow_none=True, metadata={"description": "Card above the drop position"})
    next = fields.UUID(allow_none=True, metadata={"description": "Card below the drop position"})


class CreateSubtaskSchema(BaseSchema):
    title = Text(required=True, max_length=255)


class UpdateSubtaskSchema(BaseSchema):
    title = Text(max_length=255)
    is_done = fields.Boolean(truthy={True}, falsy={False})
    order = fields.Float()
    prev = fields.UUID(allow_none=True)
    next = fields.UUID(allow_none=True)


class BoardCardsQuerySchema(BaseSchema):
    search = fields.String(metadata={"description": "Case-insensitive match on title or description"})
    filter_priority = fields.String(data_key="filter[priority]", validate=_priority)
    filter_assignee = fields.UUID(data_key="filter[assignee]")
    filter_category = fields.UUID(data_key="filter[category]")


class SubtaskSchema(BaseSchema):
    id = fields.UUID()
    card_id = fields.UUID()
    title = fields.String()
    is_done = fields.Boolean()
    order = fields.Float()


class AttachmentSchema(BaseSchema):
    id = fields.UUID()
    card_id = fields.UUID()
    name = fields.String()
    mime_type = fields.String(allow_none=True)
    url = fields.String(allow_none=True, metadata={"description": "Stored link, for link attachments"})
    file_url = fields.String(allow_none=True, metadata={"description": "Signed URL valid 15 minutes, uploads only"})
    expires_at = fields.String(allow_none=True)


class AttachmentUrlSchema(BaseSchema):
    file_url = fields.String(allow_none=True)
    expires_at = fields.String(allow_none=True)


class CardSchema(BaseSchema):
    id = fields.UUID()
    column_id = fields.UUID()
    category_id = fields.UUID(allow_none=True)
    assignee_id = fields.UUID(allow_none=True)
    assignee_name = fields.String(allow_none=True)
    assignee_avatar_url = fields.String(allow_none=True, metadata={"description": "Signed avatar URL (15 minutes) or null"})
    title = fields.String()
    description = fields.String(allow_none=True)
    priority = fields.String()
    start_date = fields.String(allow_none=True)
    end_date = fields.String(allow_none=True)
    order = fields.Float()
    archived_at = fields.String(allow_none=True)
    subtasks = fields.List(fields.Nested(SubtaskSchema))
    attachments = fields.List(fields.Nested(AttachmentSchema))
    comments = fields.List(fields.Nested(CommentSchema), metadata={"description": "Omitted for Guests"})
    activity = fields.List(fields.Nested(ActivitySchema), metadata={"description": "Omitted for Guests"})
