from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy.exc import IntegrityError

from app.blueprints.activity import repository as activity
from app.blueprints.auth import repository as repo
from app.blueprints.auth.dto import serialize_user
from app.common import rate_limiter
from app.common.auth import issue_token
from app.common.errors import Conflict, NotFound, Unauthorized, ValidationError
from app.common.ids import to_uuid
from app.common.validation import classify_identifier, is_email_shape, is_username, normalize_email, normalize_username
from app.extensions import db

_hasher = PasswordHasher()
# Verified for an unknown account so response time does not reveal whether it exists.
_DUMMY_HASH = _hasher.hash("not-a-real-password")


def duplicate_details(username, email, exclude_id=None):
    """Field name to message for each taken value (two lookups on the lower-cased values)."""
    details = {}
    other = repo.get_by_username(username)
    if other is not None and other.id != exclude_id:
        details["username"] = ["username is already taken"]
    other = repo.get_by_email(email)
    if other is not None and other.id != exclude_id:
        details["email"] = ["email is already registered"]
    return details


def create_account(full_name, username, email, password, role="member"):
    """Insert a user or raise Conflict whose details name each duplicate field. The caller commits."""
    username, email = normalize_username(username), normalize_email(email)
    details = duplicate_details(username, email)
    if details:
        raise Conflict("Username or email already registered", details=details)
    try:
        with db.session.begin_nested():
            return repo.create_user(full_name, username, email, _hasher.hash(password), role)
    except IntegrityError:
        # A race lost to a concurrent insert: the unique indexes are the final guard.
        raise Conflict("Username or email already registered", details=duplicate_details(username, email) or None)


def register(data):
    user = create_account(data["full_name"], data["username"], data["email"], data["password"], "member")
    db.session.commit()
    return {"user": serialize_user(user), "token": issue_token(user.id, user.role)}


def login(data, client_ip=None):
    kind, value = classify_identifier(data["identifier"])
    rate_limiter.check_login(value, client_ip)
    user = repo.get_by_email(value) if kind == "email" else repo.get_by_username(value)
    password_hash = user.password_hash if user is not None else _DUMMY_HASH
    try:
        _hasher.verify(password_hash, data["password"])
    except VerifyMismatchError:
        user = None
    if user is None:
        rate_limiter.record_login_failure(value, client_ip)
        raise Unauthorized("Invalid credentials")
    rate_limiter.reset_pair(value, client_ip)
    return {"user": serialize_user(user), "token": issue_token(user.id, user.role)}


def availability(username=None, email=None, client_ip=None):
    """{ "username": {"available": bool}, "email": {...} } for the supplied parameters only."""
    if username is None and email is None:
        raise ValidationError("Supply a username or an email", details={"username": ["username or email is required"]})
    rate_limiter.hit_availability(client_ip)
    result, problems = {}, {}
    if username is not None:
        value = normalize_username(username)
        if is_username(value):
            result["username"] = {"available": repo.get_by_username(value) is None}
        else:
            problems["username"] = ["username must be 3 to 30 characters: letters, digits, underscore or dot"]
    if email is not None:
        value = normalize_email(email)
        if is_email_shape(value):
            result["email"] = {"available": repo.get_by_email(value) is None}
        else:
            problems["email"] = ["email must be a valid email address"]
    if problems:
        raise ValidationError("Validation failed", details=problems)
    return result


def _me(actor):
    user = repo.get_by_id(to_uuid(actor.id))
    if user is None:
        raise NotFound("User not found")
    return user


def get_me(actor):
    return serialize_user(_me(actor))


def update_me(actor, data):
    user = _me(actor)
    user.full_name = data["full_name"]
    activity.add(user.id, "user.profile_updated", "user", user.id, {"fields": ["full_name"]})
    db.session.commit()
    return serialize_user(user)


def change_password(actor, data):
    user = _me(actor)
    rate_limiter.check_change_password(user.id)
    try:
        _hasher.verify(user.password_hash, data["current_password"])
    except VerifyMismatchError:
        rate_limiter.record_change_password_failure(user.id)
        raise ValidationError(
            "Current password is incorrect", details={"current_password": ["current password is incorrect"]}
        )
    user.password_hash = _hasher.hash(data["new_password"])
    activity.add(user.id, "user.password_changed", "user", user.id, {})
    rate_limiter.reset_change_password(user.id)
    db.session.commit()
