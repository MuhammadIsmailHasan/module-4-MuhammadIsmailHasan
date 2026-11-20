### Requirement 8: Activity Log

**User Story:** As a team member, I want an append-only history of what happened on a card and a board, so that I can trust the record of changes.

#### Acceptance Criteria

V10 changes: criterion 5 reworded (401 for a Guest; no shared route returns activity). All other criteria are unchanged from V8.

5. IF a Guest requests Card activity or a Board activity feed, THEN THE Backend SHALL return HTTP 401 and no `activity` or `activity_log` field, and no shared route returns Activity_Log data, including when the field is requested explicitly (Decision K; reworded in V10).
