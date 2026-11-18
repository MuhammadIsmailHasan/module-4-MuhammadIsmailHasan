from marshmallow import fields, validate

from app.common.fields import BaseSchema, Text

_visibility = validate.OneOf(["public", "private"], error="visibility must be public or private")


class CreateBoardSchema(BaseSchema):
    name = Text(required=True, max_length=255)
    visibility = fields.String(validate=_visibility, load_default="private")


class UpdateBoardSchema(BaseSchema):
    name = Text(max_length=255)
    visibility = fields.String(validate=_visibility)
    owner_id = fields.UUID(allow_none=True, metadata={"description": "Supervisor user id, or null to clear"})


class AddMemberSchema(BaseSchema):
    user_id = fields.UUID(required=True)


class CreateColumnSchema(BaseSchema):
    name = Text(required=True, max_length=255)


class ColumnSchema(BaseSchema):
    id = fields.UUID()
    board_id = fields.UUID()
    name = fields.String()
    order = fields.Float()


class BoardSchema(BaseSchema):
    id = fields.UUID()
    name = fields.String()
    visibility = fields.String()
    owner_id = fields.UUID(allow_none=True)
    archived_at = fields.String(allow_none=True)
    columns = fields.List(fields.Nested(ColumnSchema))
