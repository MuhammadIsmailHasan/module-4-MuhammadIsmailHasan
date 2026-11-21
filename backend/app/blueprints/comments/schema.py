from marshmallow import fields, validate

from app.common.fields import BaseSchema, Text


class CreateCommentSchema(BaseSchema):
    content = Text(required=True)


class CommentListQuerySchema(BaseSchema):
    sort = fields.String(
        validate=validate.OneOf(["latest", "popular"], error="sort must be latest or popular"),
        metadata={"description": "latest (default) or popular"},
    )


class ReplySchema(BaseSchema):
    id = fields.UUID()
    card_id = fields.UUID()
    author_id = fields.UUID()
    author_name = fields.String(allow_none=True, metadata={"description": "Display name of the author"})
    author_avatar_url = fields.String(allow_none=True, metadata={"description": "Signed avatar URL (15 minutes) or null"})
    parent_id = fields.UUID(allow_none=True)
    content = fields.String()
    is_priority = fields.Boolean()
    reply_count = fields.Integer()
    created_at = fields.String()
    can_create_card = fields.Boolean()


class CommentSchema(ReplySchema):
    replies = fields.List(fields.Nested(ReplySchema))
