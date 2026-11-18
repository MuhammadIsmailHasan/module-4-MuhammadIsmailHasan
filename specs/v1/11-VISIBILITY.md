### Requirement 11: Board Visibility and Archiving

**User Story:** As a Supervisor, Manager, or Admin, I want to control board visibility and archive boards and cards, so that guests see only what is intended and finished work stays recoverable.

#### Acceptance Criteria

1. THE Backend SHALL store each Board's `visibility` as exactly `public` or `private`.
2. WHEN a Supervisor, Manager, or Admin sets a Board's visibility, THE Backend SHALL apply the change and record it in the Activity_Log.
3. IF a Member or Guest attempts to set Board visibility, THEN THE Backend SHALL return HTTP 403.
4. WHEN a Guest requests the Board list, THE Backend SHALL return only Boards where `visibility` is `public` and `deleted_at` is null.
5. IF a Guest requests a private Board, THEN THE Backend SHALL return HTTP 403 with an error Envelope.
6. WHEN a signed-in user requests any non-deleted Board, THE Backend SHALL return the Board regardless of its `visibility`.
7. WHEN a Guest requests a public Board, THE Backend SHALL return its Columns and Cards and omit `comments` and `activity_log`.
8. WHEN a Manager or Admin archives a Board, THE Backend SHALL set the Board's `archived_at` and allow the archive to be reversed.
9. IF a Member or Supervisor attempts to archive a Board, THEN THE Backend SHALL return HTTP 403.
10. WHEN a Supervisor, Manager, or Admin archives a Card, THE Backend SHALL set the Card's `archived_at`.
