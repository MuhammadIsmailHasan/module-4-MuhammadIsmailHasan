import secrets

from flask import current_app

from app.blueprints.activity import repository as activity
from app.blueprints.auth import repository as auth_repo
from app.blueprints.auth import service as auth_service
from app.blueprints.users import repository as repo
from app.blueprints.users.dto import ROLES
from app.common.errors import Conflict, Forbidden, NotFound, ValidationError
from app.common.ids import to_uuid
from app.common.validation import normalize_email, normalize_username
from app.common import clock
from app.common.file_store import FileStore
from app.common.images import AVATAR_TYPES, MAX_AVATAR_BYTES, detect_image_type
from app.common.signing import verify_avatar_signature
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


# ---- avatar (V10, Decision R) --------------------------------------------------------------------

_store = FileStore("avatars")


def _file_error(message):
    return ValidationError(message, details={"file": [message]})


def _locked_user(actor):
    user = db.session.scalars(db.select(auth_repo.User).where(auth_repo.User.id == to_uuid(actor.id)).with_for_update()).first()
    if user is None:
        raise NotFound("User not found")
    return user


def set_avatar(actor, stream):
    """Write the new file, switch the row under a lock, then delete the old file (best effort)."""
    if stream is None:
        raise _file_error("file is required")
    data = stream.read(MAX_AVATAR_BYTES + 1)
    if not data:
        raise _file_error("file is empty")
    if len(data) > MAX_AVATAR_BYTES:
        raise _file_error("file must be at most 2 MB")
    kind = detect_image_type(data)
    if kind is None:
        raise _file_error("file must be a PNG, JPEG or WebP image")
    name = f"{secrets.token_hex(16)}.{kind}"
    _store.save(name, data)
    try:
        user = _locked_user(actor)
        old, user.avatar_path = user.avatar_path, name
        activity.add(user.id, "user.profile_updated", "user", user.id, {"fields": ["avatar"]})
        db.session.commit()
    except Exception:
        db.session.rollback()
        _store.delete(name)
        raise
    if old:
        _store.delete(old)
    return user


def clear_avatar(actor):
    user = _locked_user(actor)
    old = user.avatar_path
    if old is None:
        db.session.rollback()
        return user
    user.avatar_path = None
    activity.add(user.id, "user.profile_updated", "user", user.id, {"fields": ["avatar"]})
    db.session.commit()
    _store.delete(old)
    return user


def open_avatar(user_id, exp, sig):
    uid = to_uuid(user_id)
    if uid is None or not verify_avatar_signature(uid, exp, sig, clock.now()):
        raise Forbidden("Invalid or expired avatar link")
    user = auth_repo.get_by_id(uid)
    if user is None or not user.avatar_path:
        raise NotFound("No avatar")
    kind = user.avatar_path.rsplit(".", 1)[-1]
    return _store.path(user.avatar_path), AVATAR_TYPES[kind]
