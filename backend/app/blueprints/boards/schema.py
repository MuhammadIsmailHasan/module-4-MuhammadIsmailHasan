from marshmallow import fields, validate

from app.common.fields import BaseSchema, Text

_visibility = validate.OneOf(["public", "private"], error="visibility must be public or private")


class CreateBoardSchema(BaseSchema):
    name = Text(required=True, max_length=255)
    description = fields.String(allow_none=True, validate=validate.Length(max=500, error="description must be at most 500 characters"))
    visibility = fields.String(validate=_visibility, load_default="private")


class UpdateBoardSchema(BaseSchema):
    name = Text(max_length=255)
    description = fields.String(allow_none=True, validate=validate.Length(max=500, error="description must be at most 500 characters"))
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
    description = fields.String(allow_none=True)
    visibility = fields.String()
    owner_id = fields.UUID(allow_none=True)
    card_count = fields.Integer(metadata={"description": "Cards not deleted and not archived (board list only)"})
    done_count = fields.Integer(metadata={"description": "Of those, Cards in the Done column (board list only)"})
    overdue_count = fields.Integer(metadata={"description": "Of those, Cards past their end date and not Done (board list only)"})
    member_count = fields.Integer(metadata={"description": "Board members (board list only)"})
    archived_at = fields.String(allow_none=True)
    columns = fields.List(fields.Nested(ColumnSchema))


class MembersQuerySchema(BaseSchema):
    include = fields.String(validate=validate.OneOf(["email"]), metadata={"description": "`email` adds each member's email (board staff only)"})


class CandidateQuerySchema(BaseSchema):
    search = fields.String(metadata={"description": "At least 2 characters. Name substring, username prefix, or exact email (case-insensitive)"})


class CandidateSchema(BaseSchema):
    id = fields.UUID()
    full_name = fields.String()
    username = fields.String()
    email = fields.String()
    avatar_url = fields.String(allow_none=True)


class ShareSchema(BaseSchema):
    enabled = fields.Boolean()
    token = fields.String(allow_none=True, metadata={"description": "Secret; returned only by the share endpoints"})
    path = fields.String(allow_none=True, metadata={"description": "/shared/<token> or null"})
