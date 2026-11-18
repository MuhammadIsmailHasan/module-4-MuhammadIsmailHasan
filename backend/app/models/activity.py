from app.extensions import db
from app.models.base import TimestampMixin, uuid_fk, uuid_pk


class Comment(TimestampMixin, db.Model):
    __tablename__ = "comments"

    id = uuid_pk()
    card_id = uuid_fk("cards.id", nullable=False)
    author_id = uuid_fk("users.id", nullable=False)
    parent_id = uuid_fk("comments.id", nullable=True)
    content = db.Column(db.Text, nullable=False)
    is_priority = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())
    reply_count = db.Column(db.Integer, nullable=False, default=0, server_default="0")

    replies = db.relationship(
        "Comment", back_populates="parent", lazy="raise", order_by="Comment.created_at"
    )
    parent = db.relationship("Comment", back_populates="replies", remote_side="Comment.id", lazy="raise")


class ActivityLog(db.Model):
    """Append-only: created_at only, never updated or deleted."""

    __tablename__ = "activity_logs"

    id = uuid_pk()
    actor_id = uuid_fk("users.id", nullable=False)
    action = db.Column(db.String(100), nullable=False)
    target_type = db.Column(db.String(50), nullable=False)
    target_id = db.Column(db.UUID(as_uuid=True), nullable=False)
    # "metadata" is reserved on declarative classes, so the attribute is renamed.
    metadata_ = db.Column("metadata", db.JSON, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), nullable=False)


class Notification(TimestampMixin, db.Model):
    __tablename__ = "notifications"
    __table_args__ = (
        db.UniqueConstraint(
            "user_id", "card_id", "type", "notify_date", name="uq_notifications_user_card_type_date"
        ),
    )

    id = uuid_pk()
    user_id = uuid_fk("users.id", nullable=False)
    type = db.Column(db.Enum("assigned", "deadline", name="notification_type"), nullable=False)
    card_id = uuid_fk("cards.id", nullable=False)
    is_read = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())
    notify_date = db.Column(db.Date, nullable=False)
