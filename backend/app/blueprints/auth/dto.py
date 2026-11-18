"""Plain serializers (no marshmallow, no Flask)."""


def serialize_user(user):
    return {
        "id": str(user.id),
        "full_name": user.full_name,
        "login_identifier": user.login_identifier,
        "avatar_url": user.avatar_url,
    }


def serialize_user_admin(user):
    return {**serialize_user(user), "role": user.role}
