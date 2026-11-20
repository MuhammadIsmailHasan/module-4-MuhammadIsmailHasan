from app.extensions import db
from app.models import User


def get_by_username(username):
    return User.query.filter(db.func.lower(User.username) == username.lower()).first()


def get_by_email(email):
    return User.query.filter(db.func.lower(User.email) == email.lower()).first()


def get_by_id(user_id):
    return db.session.get(User, user_id) if user_id is not None else None


def create_user(full_name, username, email, password_hash, role="member"):
    user = User(full_name=full_name, username=username, email=email, password_hash=password_hash, role=role)
    db.session.add(user)
    db.session.flush()
    return user
