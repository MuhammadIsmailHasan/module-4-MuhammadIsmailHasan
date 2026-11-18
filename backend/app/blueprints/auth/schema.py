from marshmallow import fields

from app.common.fields import BaseSchema, Text


class RegisterSchema(BaseSchema):
    full_name = Text(required=True, max_length=255)
    login_identifier = Text(required=True, max_length=255, metadata={"description": "Case-insensitive, unique"})
    password = Text(required=True, min_length=8, strip=False, metadata={"description": "At least 8 characters"})


class LoginSchema(BaseSchema):
    login_identifier = Text(required=True, max_length=255)
    password = Text(required=True, strip=False)


class UserSchema(BaseSchema):
    id = fields.UUID()
    full_name = fields.String()
    login_identifier = fields.String()
    avatar_url = fields.String(allow_none=True)


class AdminUserSchema(UserSchema):
    role = fields.String(metadata={"description": "member, supervisor, manager or admin"})


class AuthSchema(BaseSchema):
    user = fields.Nested(UserSchema)
    token = fields.String(metadata={"description": "JWT, valid 24 hours"})
