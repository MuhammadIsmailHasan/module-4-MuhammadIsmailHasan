from marshmallow import RAISE, fields

from app.common.fields import BaseSchema, Email, Text, Username


class RegisterSchema(BaseSchema):
    full_name = Text(required=True, max_length=255)
    username = Username(required=True)
    email = Email(required=True)
    password = Text(required=True, min_length=8, strip=False, metadata={"description": "At least 8 characters"})


class LoginSchema(BaseSchema):
    identifier = Text(required=True, max_length=255, metadata={"description": "Username or email, case-insensitive"})
    password = Text(required=True, strip=False)


class UpdateMeSchema(BaseSchema):
    """Only full_name; any other field (username, email, role, avatar_url, ...) is a 400."""

    class Meta:
        unknown = RAISE

    full_name = Text(required=True, max_length=255)


class ChangePasswordSchema(BaseSchema):
    current_password = Text(required=True, strip=False)
    new_password = Text(required=True, min_length=8, strip=False, metadata={"description": "At least 8 characters"})


class AvailabilityQuerySchema(BaseSchema):
    username = fields.String()
    email = fields.String()


class AvailabilityEntrySchema(BaseSchema):
    available = fields.Boolean()


class AvailabilitySchema(BaseSchema):
    username = fields.Nested(AvailabilityEntrySchema)
    email = fields.Nested(AvailabilityEntrySchema)


class UserSchema(BaseSchema):
    id = fields.UUID()
    full_name = fields.String()
    username = fields.String()
    email = fields.String()
    avatar_url = fields.String(allow_none=True)


class MemberSchema(BaseSchema):
    id = fields.UUID()
    full_name = fields.String()
    username = fields.String()
    avatar_url = fields.String(allow_none=True)


class MemberWithEmailSchema(MemberSchema):
    email = fields.String(metadata={"description": "Only with ?include=email, for board staff"})


class AdminUserSchema(UserSchema):
    role = fields.String(metadata={"description": "member, supervisor, manager or admin"})


class AuthSchema(BaseSchema):
    user = fields.Nested(UserSchema)
    token = fields.String(metadata={"description": "JWT, valid 24 hours"})
