---
inclusion: always
---

# Data Model Steering

- **Rule:** Core entities are `User, Board, Column, Card, Category, Subtask,
  Comment, ActivityLog, Notification, Attachment`; every entity has
  `id (UUID)`, `created_at`, `updated_at`; `Board` and `Card` additionally have
  `deleted_at` and `archived_at`.
  **Rationale:** One shared shape simplifies serialization and gives every
  entity an audit trail.
  **Example:**
  `Card(id, column_id, category_id, title, description, priority, start_date, end_date, order: Float, assignee_id, created_at, updated_at, deleted_at, archived_at)`.

- **Rule:** `Category` is `id, board_id, name, color (nullable), created_at,
  updated_at`, cascade-deleted with its board; `Card.category_id` is a
  nullable FK to `Category`.
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
  supervisor, manager, or admin roles.
  **Rationale:** This is exactly what "guests see public boards only" and
  "supervisor can make public/private" need.
  **Example:** guest board listing: `WHERE visibility = 'public' AND deleted_at IS NULL`.

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
