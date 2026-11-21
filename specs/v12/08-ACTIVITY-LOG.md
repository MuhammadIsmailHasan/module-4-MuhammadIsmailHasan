# Activity log, V12 changes

New actions (no column change; one row per saved request, Requirement 25 criteria 11 and 12): `board.invite_enabled`, `board.invite_regenerated`, `board.invite_disabled`, `board.join_requested`, `board.join_rejected`, `card.subtask_added`, `card.subtask_updated`, `card.subtask_removed`, `card.attachment_added`, `card.attachment_removed`, and `comment.deleted` (target `card`, no comment text). `board.member_added` gains the optional `metadata.via` `join_request`. `board.visibility_changed` is never written. A `PATCH /api/cards/{id}` that changes nothing writes no row. The invite and share tokens never appear in `metadata`.

### Requirement 8 criteria with V12 labels

Criteria of Requirement 8 that V12 changed. Each line is the full V1 to V11 criterion followed by its V12 label; the label wins.

9. THE Backend SHALL store, in the `metadata` of each new Activity_Log row, the names needed to read it without a lookup: `card_title` on every Card event; for `card.updated`, `changes` as an object of `{ "from": ..., "to": ... }` per changed field among `title`, `priority`, `start_date`, `end_date`, and `category` (the Category's name), with a changed `description` recorded by field name only; `from_column_name` and `to_column_name` on `card.moved` beside the ids; `assignee_name` on `card.assigned`; `title` on Subtask events; and `name` on Attachment events (Decision I). (V12: one `card.updated` row per saved request, and new Subtask and Attachment actions, Requirement 25, criteria 11 and 12.)
