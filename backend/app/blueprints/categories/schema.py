from marshmallow import fields

from app.common.fields import BaseSchema, Text


class CreateCategorySchema(BaseSchema):
    name = Text(required=True, max_length=255)
    color = fields.String(allow_none=True)


class UpdateCategorySchema(BaseSchema):
    name = Text(max_length=255)
    color = fields.String(allow_none=True)


class CategorySchema(BaseSchema):
    id = fields.UUID()
    board_id = fields.UUID()
    name = fields.String()
    color = fields.String(allow_none=True)
