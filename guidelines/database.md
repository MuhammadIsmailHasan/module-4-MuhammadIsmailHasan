# Database Guidelines

Coding standards for SQLAlchemy models and migrations.

---

**Rule:** Every table has `id (UUID, primary key)`, `created_at`, `updated_at`;
`Board` and `Card` additionally have `deleted_at` and `archived_at` (all
nullable). `ActivityLog` and `RateLimitAttempt` are append-only and carry
`created_at` only. `User.username` and `User.email` are unique on their
lower-cased value; `Board.share_token` (the public link) and `Board.invite_token` (V12) are
nullable unique strings; `Board` has no `visibility` column (V12);
`BoardJoinRequest` has a partial unique index on `(board_id, user_id)` where
`status = 'pending'` and holds no copy of the requester's email (the pending list joins `User`); `Notification` deduplicates with three partial unique
indexes because `card_id` is nullable.

**Rationale:** Uniform audit columns across every table, and exactly the
shape the service layer's soft-delete/archive logic expects everywhere.

**Example:**
```python
class Card(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    deleted_at = db.Column(db.DateTime, nullable=True)
    archived_at = db.Column(db.DateTime, nullable=True)
    order = db.Column(db.Float, nullable=False)
```

---

**Rule:** Foreign keys default to `RESTRICT` (no implicit cascade delete),
except `ActivityLog`, `Notification`, `Subtask`, and `Category`, which
`CASCADE` on delete of their owning card/board.

**Rationale:** Prevents accidentally wiping history on an unrelated delete,
while still letting archiving/cleanup remove rows that only exist to
describe a now-gone parent.

**Example:**
```python
card_id = db.Column(UUID, db.ForeignKey("cards.id", ondelete="CASCADE"))  # on Subtask, Notification
board_id = db.Column(UUID, db.ForeignKey("boards.id", ondelete="CASCADE"))  # on Category
```

---

**Rule:** Enum-like columns (`priority`, `role`, `join_request.status`,
`notification.type`; `visibility` was removed in V12) are DB-level enums or explicitly constrained strings —
never free text.

**Rationale:** Guarantees only valid values ever reach filter and analytics
queries.

**Example:**
```python
priority = db.Column(db.Enum("high", "medium", "low", name="priority_enum"), nullable=False)
```

---

**Rule:** Every query against `Board` or `Card` filters out soft-deleted rows
by default (`deleted_at IS NULL`), implemented once as a model-level default
scope or query helper, not repeated ad hoc in every service function.

**Rationale:** A single missed `WHERE deleted_at IS NULL` would resurrect
deleted records in listings; centralizing it removes that risk.

**Example:**
```python
def active_cards_query():
    return Card.query.filter(Card.deleted_at.is_(None))
```

---

**Rule:** `Attachment` rows store either a `url` or a `file_path`, enforced
at the application layer (schema validation), with exactly one of the two
populated.

**Rationale:** Matches the requirement that an attachment is a link *or* a
file, not an ambiguous mix.

**Example:**
```python
class AttachmentCreateSchema(Schema):
    url = fields.Url(allow_none=True)
    file_path = fields.Str(allow_none=True)

    @validates_schema
    def exactly_one(self, data, **kwargs):
        if bool(data.get("url")) == bool(data.get("file_path")):
            raise ValidationError("Provide exactly one of url or file_path")
```

---

**Rule:** `Comment.parent_id` is a nullable self-referential foreign key; a
`CHECK`-equivalent (enforced in the service layer, since cross-row checks
aren't expressible as a column `CHECK`) guarantees a comment whose
`parent_id` is set can never be referenced as another comment's `parent_id`.

**Rationale:** The schema alone can't express "max depth 2" — that has to be
guarded at the point of insert, but the column shape (self-FK, nullable)
still has to support it cleanly.

**Example:**
```python
class Comment(db.Model):
    parent_id = db.Column(UUID, db.ForeignKey("comments.id"), nullable=True)
    is_priority = db.Column(db.Boolean, default=False, nullable=False)
    reply_count = db.Column(db.Integer, default=0, nullable=False)  # drives "Popular" sort; no like table exists
```

---

**Rule:** `Category` belongs to exactly one `Board` (`board_id`, not
nullable); `Card.category_id` is a nullable FK to `Category` — a card can
have zero or one category.

**Rationale:** "Every board has its own category" means the foreign key has
to point at a board, not sit as a free global table.

**Example:**
```python
class Category(db.Model):
    board_id = db.Column(UUID, db.ForeignKey("boards.id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    color = db.Column(db.String(16), nullable=True)

# on Card
category_id = db.Column(UUID, db.ForeignKey("categories.id"), nullable=True)
```

---

**Rule:** `Subtask` is its own table (`id, card_id, title, is_done, order,
created_at, updated_at`) rather than a JSON column on `Card`.

**Rationale:** A JSON blob can't be queried, indexed, or reordered with the
same `Float` midpoint trick the rest of the app already uses for ordering —
a real table keeps subtasks consistent with how cards/columns work.

**Example:**
```python
class Subtask(db.Model):
    card_id = db.Column(UUID, db.ForeignKey("cards.id", ondelete="CASCADE"))
    title = db.Column(db.String(255), nullable=False)
    is_done = db.Column(db.Boolean, default=False, nullable=False)
    order = db.Column(db.Float, nullable=False)
```
---
**Rule:** A column that points to a stored file holds only the generated file
name (`User.avatar_path`), never a URL or a client file name; the URL a client
sees is computed per response.
**Rationale:** A stored URL expires or leaks; a bare name cannot be turned
into a path outside the upload folder.
**Example:** `avatar_path = db.Column(db.String(64), nullable=True)` holds
`3f9c...e1.png`, and the API returns a signed `avatar_url` or `null`. A lookup that only needs a name and an avatar selects `id, full_name, avatar_path` columns, not the user entity, so `email` is never loaded.
