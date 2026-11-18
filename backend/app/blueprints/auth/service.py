from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.blueprints.auth import repository as repo
from app.blueprints.auth.dto import serialize_user
from app.common.auth import issue_token
from app.common.errors import Conflict, Unauthorized
from app.extensions import db

_hasher = PasswordHasher()


def register(data):
    full_name, login, password = data["full_name"], data["login_identifier"], data["password"]
    if repo.get_by_login(login) is not None:
        raise Conflict("login_identifier already registered")
    user = repo.create_user(full_name, login, _hasher.hash(password), "member")
    db.session.commit()
    return {"user": serialize_user(user), "token": issue_token(user.id, user.role)}


def login(data):
    login_id, password = data["login_identifier"], data["password"]
    user = repo.get_by_login(login_id)
    if user is None:
        raise Unauthorized("Invalid credentials")
    try:
        _hasher.verify(user.password_hash, password)
    except VerifyMismatchError:
        raise Unauthorized("Invalid credentials")
    return {"user": serialize_user(user), "token": issue_token(user.id, user.role)}
