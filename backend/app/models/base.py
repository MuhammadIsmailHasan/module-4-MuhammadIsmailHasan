import uuid

from sqlalchemy.dialects.postgresql import UUID

from app.extensions import db


def uuid_pk():
    return db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


def uuid_fk(target, **kwargs):
    return db.Column(UUID(as_uuid=True), db.ForeignKey(target), **kwargs)


class TimestampMixin:
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now(),
        onupdate=db.func.now(),
        nullable=False,
    )
