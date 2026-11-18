### Requirement 8: Activity Log

**User Story:** As a team member, I want an append-only history of what happened on a card and a board, so that I can trust the record of changes.

#### Acceptance Criteria

1. WHEN a state-changing action succeeds, THE Backend SHALL insert exactly one Activity_Log row with `actor_id`, `action`, `target_type`, `target_id`, `metadata`, and `created_at` in the same transaction as the change.
2. THE Backend SHALL never update or delete an Activity_Log row after insertion.
3. WHEN a Member, Supervisor, Manager, or Admin requests a Card's activity, THE Backend SHALL return the rows where `target_type` is `card` and `target_id` is that Card's id.
4. WHEN a Member, Supervisor, Manager, or Admin requests a Board's activity feed, THE Backend SHALL return every row for the Cards and Columns belonging to that Board.
5. IF a Guest requests Card activity or a Board activity feed, THEN THE Backend SHALL return no `activity` or `activity_log` field, including on direct calls and when the field is requested explicitly.
6. WHEN a user opens Activity from the Sidebar nav, THE Frontend SHALL open the Side_Panel on the Activity view.
7. WHERE the Card response omits `activity`, THE Frontend SHALL omit the Card activity section.
