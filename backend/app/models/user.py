from app.extensions import db
from app.models.base import TimestampMixin, uuid_pk


class User(TimestampMixin, db.Model):
    __tablename__ = "users"

    id = uuid_pk()
    full_name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.Enum("member", "supervisor", "manager", "admin", name="user_role"),
        nullable=False,
        default="member",
    )
    avatar_path = db.Column(db.String(64), nullable=True)


# Case-insensitive uniqueness (Decision M).
db.Index("uq_users_username_lower", db.func.lower(User.username), unique=True)
db.Index("uq_users_email_lower", db.func.lower(User.email), unique=True)
