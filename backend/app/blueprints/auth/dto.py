"""Plain serializers (no marshmallow, no Flask)."""


def _avatar(user):
    from app.common import clock
    from app.common.signing import avatar_url

    return avatar_url(user.id, clock.now()) if user.avatar_path else None


def serialize_user(user):
    return {
        "id": str(user.id),
        "full_name": user.full_name,
        "username": user.username,
        "email": user.email,
        "avatar_url": _avatar(user),
    }


def serialize_user_admin(user):
    return {**serialize_user(user), "role": user.role}


def serialize_member(user):
    """A person as other users see them: never the email."""
    return {"id": str(user.id), "full_name": user.full_name, "username": user.username, "avatar_url": _avatar(user)}


def serialize_candidate(user):
    """Candidate rows go to board staff only, so the email is included (Decision S)."""
    return {**serialize_member(user), "email": user.email}
