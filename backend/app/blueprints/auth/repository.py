from app.extensions import db
from app.models import User


def get_by_login(login_identifier):
    return User.query.filter(db.func.lower(User.login_identifier) == login_identifier.lower()).first()


def get_by_id(user_id):
    return db.session.get(User, user_id) if user_id is not None else None


def create_user(full_name, login_identifier, password_hash, role="member"):
    user = User(full_name=full_name, login_identifier=login_identifier, password_hash=password_hash, role=role)
    db.session.add(user)
    db.session.flush()
    return user
