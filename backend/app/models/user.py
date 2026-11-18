from app.extensions import db
from app.models.base import TimestampMixin, uuid_pk


class User(TimestampMixin, db.Model):
    __tablename__ = "users"

    id = uuid_pk()
    full_name = db.Column(db.String(255), nullable=False)
    login_identifier = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.Enum("member", "supervisor", "manager", "admin", name="user_role"),
        nullable=False,
        default="member",
    )
    avatar_url = db.Column(db.String(1024), nullable=True)


# Case-insensitive uniqueness (Decision C).
db.Index("uq_users_login_identifier_lower", db.func.lower(User.login_identifier), unique=True)
