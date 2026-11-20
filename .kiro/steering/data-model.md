---
inclusion: always
---

# Data Model Steering

- **Rule:** Core entities are `User, Board, BoardMember, Column, Card, Category, Subtask,
  Comment, ActivityLog, Notification, Attachment`; every entity has
  `id (UUID)`, `created_at`, `updated_at`; `Board` and `Card` additionally have
  `deleted_at` and `archived_at`. The exceptions are `ActivityLog` and
  `RateLimitAttempt`, which have `created_at` only (append-only; rows are only
  inserted and deleted).
  **Rationale:** One shared shape simplifies serialization and gives every
  entity an audit trail.
  **Example:**
  `Card(id, column_id, category_id, title, description, priority, start_date, end_date, order: Float, assignee_id, created_at, updated_at, deleted_at, archived_at)`.

- **Rule:** `Category` is `id, board_id, name, color (nullable), created_at,
  updated_at`, scoped to its board and unique by case-insensitive `name`
  within that board; boards are never hard-deleted, so categories simply
  become unreachable once their board is soft-deleted. `Card.category_id` is
  a nullable FK to `Category`.
  **Rationale:** Scoping categories to a board (not global) is what "every
  board has its own category" means at the schema level.
  **Example:** `Category(board_id=board.id, name="Design", color="#7c5cff")`.

- **Rule:** `Card` has separate `start_date` and `end_date` columns (both
  nullable dates) — not one free-text "due" field.
  **Rationale:** The deadline-notification job and the "reached its final day"
  rule both key off a real `end_date` column, not a display string.
  **Example:** `end_date = db.Column(db.Date, nullable=True)`.

- **Rule:** `ActivityLog` rows are append-only: `actor_id, action, target_type,
  target_id, metadata (JSON), created_at` — never updated or deleted after
  insert. A card's own activity is `WHERE target_type='card' AND target_id=?`;
  the board-wide feed is every row for cards/columns belonging to that board.
  **Rationale:** The activity log is only trustworthy as a history if nothing
  can rewrite it after the fact.
  **Example:** moving a card logs
  `{ "action": "card.moved", "from_column": "...", "to_column": "..." }`.

- **Rule:** `Board.visibility` is an enum `public | private`, mutable only by
  supervisor, manager, or admin roles. A signed-in user's board list is the
  public boards plus the boards they can access; a guest has no board list.
  **Rationale:** "Supervisor can make public/private" and "private blocks
  unrelated signed-in users" both key off this column.
  **Example:** member board listing: `WHERE deleted_at IS NULL AND (visibility = 'public' OR <owner or member or manager/admin>)`.
- **Rule:** `Board.share_token` is a nullable, unique string (43 URL-safe
  characters from `secrets.token_urlsafe(32)`); null means sharing is off. It
  is returned only by the share endpoints and never written to
  `ActivityLog.metadata` or logs.
  **Rationale:** The token is the credential for the read-only shared view, so
  it must be unguessable and must not leak into other responses.
  **Example:** `share_token = db.Column(db.String(64), nullable=True)` plus a unique index.

- **Rule:** `Attachment` stores either a `url` (link) or a `file_path` +
  `mime_type` (upload), never both empty.
  **Rationale:** An attachment is a link **or** a file — the schema should
  make the other case unrepresentable, not just unused.
  **Example:** `Attachment(card_id, url=None, file_path="uploads/spec.pdf", mime_type="application/pdf")`.

- **Rule:** `Subtask` is `id, card_id, title, is_done (bool, default false),
  order (Float), created_at, updated_at` — no assignee, no dates.
  **Rationale:** A subtask is a checklist item, not a second card; keeping its
  columns minimal is what keeps it fast to add and check off.
  **Example:** `Subtask(card_id=card.id, title="Write migration", is_done=False, order=1.0)`.

- **Rule:** `Comment` has a self-referential nullable `parent_id`, plus
  `is_priority (bool, default false)` and a denormalized `reply_count (int,
  default 0)`. There is no like/vote table — popularity is reply count, not
  likes.
  **Rationale:** `parent_id` gives the 2-level tree, `is_priority` gives the
  manager-set sort pin, and a denormalized `reply_count` means sorting by
  popularity doesn't require a `COUNT()` join on every page load.
  **Example:** inserting a reply does
  `parent.reply_count += 1` in the same transaction as the insert.

- **Rule:** A `Comment` with a non-null `parent_id` can never itself be the
  `parent_id` of another comment (max depth 2), enforced at the service layer
  before insert, not just in the UI.
  **Rationale:** The depth cap has to hold even against a direct API call, not
  only against the "Reply" button being hidden on replies.
  **Example:** `if parent.parent_id is not None: raise ValidationError(...)`.

- **Rule:** `progress` (0–10 integer) and `views_count` (integer, default 0)
  are **stretch, non-MVP** columns on `Card` — carried over from the
  prototype by request, built only after every column above is in place and
  working. (`category` is no longer stretch — it's the real `Category`
  entity above, requested as a full feature.)
  **Rationale:** These two weren't in the original feature list; marking
  them explicitly stretch keeps them from being prioritized over the required
  fields (priority, dates, attachments, subtasks, category, assignee).
  **Example:** `progress = db.Column(db.Integer, nullable=True)` added in a
  later migration, not the first one.

- **Rule:** `Board.owner_id` is a nullable FK to `User` (the supervisor who
  owns the board). Supervisor analytics access and board-ownership checks key
  off it.
  **Rationale:** "A supervisor sees analytics only for boards they own" needs
  a real column, not an inferred relationship.
  **Example:** `owner_id = db.Column(UUID(as_uuid=True), db.ForeignKey("user.id"), nullable=True)`.

- **Rule:** `Notification` has a `notify_date` (Date) and a unique constraint
  on `(user_id, card_id, type, notify_date)`.
  **Rationale:** The deadline job can run more than once a day (retries,
  restarts); the constraint makes reruns insert nothing new instead of
  notifying an assignee twice.
  **Example:** `db.UniqueConstraint("user_id", "card_id", "type", "notify_date")`.

- **Rule:** When averaging `order` values leaves a gap below `1e-6` between
  neighbours, the move service renumbers that column's cards as `1.0, 2.0, ...`
  in the same transaction.
  **Rationale:** Float averaging runs out of precision after roughly 50
  consecutive drops into the same gap; a rare in-column renumber keeps the
  Float-order approach working.
  **Example:** dropping between `1.0` and `1.0000005` triggers a renumber, then
  the card is placed at the midpoint of its new neighbours.

- **Rule:** `User` has a unique, case-insensitive `username` (3 to 30 characters
  from `a-z 0-9 _ .`, stored lowercase, not null) and a unique,
  case-insensitive `email` (valid format, at most 255, stored lowercase;
  nullable in the database only for migrated legacy accounts). There is no
  `login_identifier` column. `avatar_path` is a nullable generated file name
  (`<32 hex>.png|jpg|webp`) under `UPLOAD_DIR/avatars/`, never a URL; the API's
  `avatar_url` is computed from it as a signed, time-limited URL.
  **Rationale:** Two real columns give field-level validation and errors; the
  nullable email exists only so the V10 migration can keep username-only
  accounts until they add an address.
  **Example:** `db.Index("uq_users_username_lower", db.func.lower(User.username), unique=True)` and `db.Index("uq_users_email_lower", db.func.lower(User.email), unique=True)`.
- **Rule:** `RateLimitAttempt` is `id, scope (login_pair | login_ip |
  availability), key_hash, created_at`, with an index on `(scope, key_hash,
  created_at)`. `key_hash` is a keyed hash, never a plaintext identifier,
  email, or address.
  **Rationale:** A shared table makes the limiter correct across workers
  without Redis, and hashing keeps personal data out of it.
  **Example:** `RateLimitAttempt(scope="login_pair", key_hash=hmac_hex("ratelimit:pair:" + identifier + "|" + ip))`.

- **Rule:** `BoardMember` is a join entity `(id, board_id, user_id, created_at,
  updated_at)` with a unique `(board_id, user_id)`; it records users attached
  to a board beyond its `owner_id`. Supervisor access to a board is
  `owner OR BoardMember`; a Member's access to a private board needs
  `BoardMember`. Manager and Admin need no membership.
  **Rationale:** "Private" must gate unrelated signed-in users, which needs a
  real relationship to check.
  **Example:** `BoardMember(board_id=board.id, user_id=member.id)`.

- **Rule:** Card and Subtask `order` has boundary rules: first position is
  `min_order - 1`, last is `max_order + 1`, and Subtask reordering uses the
  same averaging and renumber rule as Card ordering. Child rows (Subtask,
  Attachment, Comment) have no `deleted_at`; they are hidden by joining the
  parent Card's `deleted_at`.
  **Rationale:** Closes the edge cases the averaging rule alone leaves open
  and avoids duplicating soft-delete state.
  **Example:** dropping at the top of a column whose first card is `1.0`
  gives order `0.0`.

- **Rule:** Models declare SQLAlchemy relationships only for real cross-table
  reads: `Board.columns`, `Board.members`, `Card.subtasks`, `Card.attachments`,
  `Comment.replies`, each paired with `back_populates` (never `backref`) and
  declared `lazy="raise"`, with no `cascade="all, delete"` (boards and cards are
  never hard-deleted). Models carry no `to_dict()` or other serialization
  method.
  **Rationale:** `lazy="raise"` turns an accidental lazy load into a test
  failure instead of a hidden N+1 query that threatens the 300 ms p95 target;
  serialization depends on the viewer (guest privacy, `can_create_card`, signed
  URLs), so it belongs to marshmallow schemas, not the model.
  **Example:** `subtasks = db.relationship("Subtask", back_populates="card", lazy="raise", order_by="Subtask.order")`.

- **Rule:** `Board` has a nullable `description` (at most 500 characters,
  V8 round 5). The board list response carries computed `card_count`,
  `done_count`, `overdue_count`, and `member_count`; they are never stored.
  **Rationale:** Home tiles need a short summary per board without a query per
  board, and derived counts stored as columns would drift.
  **Example:** `Board(id, name, description, visibility, owner_id, created_at, updated_at, deleted_at, archived_at)`.

