from app.extensions import db
from app.models.base import TimestampMixin, uuid_fk, uuid_pk


class Category(TimestampMixin, db.Model):
    __tablename__ = "categories"

    id = uuid_pk()
    board_id = uuid_fk("boards.id", nullable=False)
    name = db.Column(db.String(255), nullable=False)
    color = db.Column(db.String(64), nullable=True)


# Unique by case-insensitive name within a board.
db.Index("uq_categories_board_name_lower", Category.board_id, db.func.lower(Category.name), unique=True)


class Card(TimestampMixin, db.Model):
    __tablename__ = "cards"
    __table_args__ = (
        db.CheckConstraint(
            "start_date IS NULL OR end_date IS NULL OR end_date >= start_date",
            name="ck_cards_end_after_start",
        ),
    )

    id = uuid_pk()
    column_id = uuid_fk("columns.id", nullable=False)
    category_id = db.Column(
        db.UUID(as_uuid=True), db.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    assignee_id = uuid_fk("users.id", nullable=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(
        db.Enum("high", "medium", "low", name="card_priority"),
        nullable=False,
        default="medium",
    )
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    order = db.Column(db.Float, nullable=False)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)
    archived_at = db.Column(db.DateTime(timezone=True), nullable=True)
    # Stretch columns (progress, views_count) are intentionally left for a later migration.


class Subtask(TimestampMixin, db.Model):
    __tablename__ = "subtasks"

    id = uuid_pk()
    card_id = uuid_fk("cards.id", nullable=False)
    title = db.Column(db.String(255), nullable=False)
    is_done = db.Column(db.Boolean, nullable=False, default=False, server_default=db.false())
    order = db.Column(db.Float, nullable=False)


class Attachment(TimestampMixin, db.Model):
    __tablename__ = "attachments"
    __table_args__ = (
        db.CheckConstraint("url IS NOT NULL OR file_path IS NOT NULL", name="ck_attachments_url_or_file"),
    )

    id = uuid_pk()
    card_id = uuid_fk("cards.id", nullable=False)
    name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(2048), nullable=True)
    file_path = db.Column(db.String(1024), nullable=True)
    mime_type = db.Column(db.String(255), nullable=True)
