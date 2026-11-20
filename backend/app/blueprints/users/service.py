from app.blueprints.activity import repository as activity
from app.blueprints.auth import repository as auth_repo
from app.blueprints.auth import service as auth_service
from app.blueprints.users import repository as repo
from app.blueprints.users.dto import ROLES
from app.common.errors import Conflict, NotFound, ValidationError
from app.common.ids import to_uuid
from app.common.validation import normalize_email, normalize_username
from app.extensions import db


def list_users():
    return repo.list_all()


def _role(value):
    if value not in ROLES:
        raise ValidationError("role must be one of: " + ", ".join(ROLES))
    return value


def create_user(actor, data):
    role = _role(data.get("role", "member"))
    user = auth_service.create_account(data["full_name"], data["username"], data["email"], data["password"], role)
    activity.add(to_uuid(actor.id), "user.created", "user", user.id, {"role": role})
    db.session.commit()
    return user


def update_user(actor, user_id, data):
    uid = to_uuid(user_id)
    user = auth_repo.get_by_id(uid) if uid else None
    if user is None:
        raise NotFound("User not found")
    changed = []
    if "full_name" in data:
        if not isinstance(data["full_name"], str) or not data["full_name"].strip():
            raise ValidationError("full_name is required")
        user.full_name = data["full_name"].strip()
        changed.append("full_name")
    if "username" in data or "email" in data:
        username = normalize_username(data.get("username", user.username))
        email = normalize_email(data.get("email", user.email))
        details = auth_service.duplicate_details(username, email, exclude_id=user.id)
        if details:
            raise Conflict("Username or email already registered", details=details)
        for field, value in (("username", username), ("email", email)):
            if getattr(user, field) != value:
                setattr(user, field, value)
                changed.append(field)
    if changed:
        activity.add(to_uuid(actor.id), "user.updated", "user", user.id, {"fields": changed})
    if "role" in data:
        role = _role(data["role"])
        if role != user.role:
            activity.add(
                to_uuid(actor.id), "user.role_changed", "user", user.id, {"from": user.role, "to": role}
            )
            user.role = role
    db.session.commit()
    return user
