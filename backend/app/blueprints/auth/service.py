from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy.exc import IntegrityError

from app.blueprints.auth import repository as repo
from app.blueprints.auth.dto import serialize_user
from app.common.auth import issue_token
from app.common.errors import Conflict, Unauthorized, ValidationError
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


def login(data):
    kind, value = classify_identifier(data["identifier"])
    user = repo.get_by_email(value) if kind == "email" else repo.get_by_username(value)
    password_hash = user.password_hash if user is not None else _DUMMY_HASH
    try:
        _hasher.verify(password_hash, data["password"])
    except VerifyMismatchError:
        user = None
    if user is None:
        raise Unauthorized("Invalid credentials")
    return {"user": serialize_user(user), "token": issue_token(user.id, user.role)}


def availability(username=None, email=None):
    """{ "username": {"available": bool}, "email": {...} } for the supplied parameters only."""
    if username is None and email is None:
        raise ValidationError("Supply a username or an email", details={"username": ["username or email is required"]})
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
