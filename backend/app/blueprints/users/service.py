from argon2 import PasswordHasher

from app.blueprints.activity import repository as activity
from app.blueprints.auth import repository as auth_repo
from app.blueprints.users import repository as repo
from app.blueprints.users.dto import ROLES
from app.common.errors import Conflict, NotFound, ValidationError
from app.common.ids import to_uuid
from app.extensions import db

_hasher = PasswordHasher()


def list_users():
    return repo.list_all()


def _role(value):
    if value not in ROLES:
        raise ValidationError("role must be one of: " + ", ".join(ROLES))
    return value


def create_user(actor, data):
    full_name, login, password = data["full_name"], data["login_identifier"], data["password"]
    role = _role(data.get("role", "member"))
    if auth_repo.get_by_login(login):
        raise Conflict("login_identifier already registered")
    user = auth_repo.create_user(full_name, login, _hasher.hash(password), role)
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
    if "login_identifier" in data:
        login = data["login_identifier"]
        if not isinstance(login, str) or not login.strip() or len(login.strip()) > 255:
            raise ValidationError("login_identifier is invalid")
        existing = auth_repo.get_by_login(login.strip())
        if existing is not None and existing.id != user.id:
            raise Conflict("login_identifier already registered")
        user.login_identifier = login.strip()
        changed.append("login_identifier")
    if "avatar_url" in data:
        user.avatar_url = data["avatar_url"]
        changed.append("avatar_url")
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
