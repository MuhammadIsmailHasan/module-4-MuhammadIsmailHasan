from marshmallow import fields, validate

from app.blueprints.auth.schema import RegisterSchema
from app.blueprints.users.dto import ROLES
from app.common.fields import BaseSchema, Text

_role = validate.OneOf(ROLES, error="role must be one of: " + ", ".join(ROLES))


class CreateUserSchema(RegisterSchema):
    role = fields.String(validate=_role, load_default="member")


class UpdateUserSchema(BaseSchema):
    full_name = Text(max_length=255)
    login_identifier = Text(max_length=255)
    avatar_url = fields.String(allow_none=True)
    role = fields.String(validate=_role)
