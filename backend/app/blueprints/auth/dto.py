"""Plain serializers (no marshmallow, no Flask)."""


def serialize_user(user):
    return {
        "id": str(user.id),
        "full_name": user.full_name,
        "username": user.username,
        "email": user.email,
        "avatar_url": None,  # signed avatar URL arrives with the avatar endpoints (task 33.29)
    }


def serialize_user_admin(user):
    return {**serialize_user(user), "role": user.role}


def serialize_member(user):
    """A person as other users see them: never the email."""
    return {"id": str(user.id), "full_name": user.full_name, "username": user.username, "avatar_url": None}


def serialize_candidate(user):
    """Candidate rows go to board staff only, so the email is included (Decision S)."""
    return {**serialize_member(user), "email": user.email}
