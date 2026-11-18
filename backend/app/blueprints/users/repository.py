from app.extensions import db
from app.models import User


def list_all():
    return User.query.order_by(User.full_name, User.id).all()
