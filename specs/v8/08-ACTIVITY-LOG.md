### Requirement 8: Activity Log

**User Story:** As a team member, I want an append-only history of what happened on a card and a board, so that I can trust the record of changes.

#### Acceptance Criteria

1. WHEN a state-changing action succeeds, THE Backend SHALL insert exactly one Activity_Log row with `actor_id`, `action`, `target_type`, `target_id`, `metadata`, and `created_at` in the same transaction as the change.
2. THE Backend SHALL never update or delete an Activity_Log row after insertion.
3. WHEN a signed-in user with Board_Access to a Card's Board requests the Card's activity, THE Backend SHALL return the rows where `target_type` is `card` and `target_id` is that Card's id (Decision A).
4. WHEN a signed-in user with Board_Access to a Board requests the Board's activity feed, THE Backend SHALL return every row for the Cards and Columns belonging to that Board (Decision A).
5. IF a Guest requests Card activity or a Board activity feed, THEN THE Backend SHALL return no `activity` or `activity_log` field, including on direct calls and when the field is requested explicitly.
6. WHEN a user opens Activity from the Sidebar nav, THE Frontend SHALL open the Side_Panel on the Activity view.
7. WHERE the Card response omits `activity`, THE Frontend SHALL omit the Card activity section.
8. THE Backend SHALL include the actor's full name as `actor_name` on every returned Activity_Log row, loading names for all actors of a response in one query, and THE Frontend SHALL show that name and never a placeholder for a known actor (Decision I).
9. THE Backend SHALL store, in the `metadata` of each new Activity_Log row, the names needed to read it without a lookup: `card_title` on every Card event; for `card.updated`, `changes` as an object of `{ "from": ..., "to": ... }` per changed field among `title`, `priority`, `start_date`, `end_date`, and `category` (the Category's name), with a changed `description` recorded by field name only; `from_column_name` and `to_column_name` on `card.moved` beside the ids; `assignee_name` on `card.assigned`; `title` on Subtask events; and `name` on Attachment events (Decision I).
10. THE Frontend SHALL write each Activity_Log row as the actor, the action, the object, and, for a move or a change, where it went, for example "Manager moved "Card title" from [Todo] to [In Progress]" or "Manager changed the priority of "Card title" from Medium to High", with the actor in bold, the object in quotes, Column names as badges, and the time under the sentence, and SHALL fall back to generic wording for rows written before Decision I that lack these names (Decision I).
11. WHEN a signed-in user with Board_Access requests `GET /api/boards/{id}/activity` or `GET /api/cards/{id}/activity` with `limit` and optional `before`, THE Backend SHALL return at most `limit` rows (default 20, at most 100) older than the row `before` in the same order and response shape as today; IF `before` names a row outside that feed, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR` (Decision J).
12. THE Frontend SHALL load the first page of an activity list sized to fill the visible area and show a Load more action that requests the next page with `before` set to the last shown row, hiding the action once a page returns fewer rows than `limit` (Decision J).
