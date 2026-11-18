### Requirement 11: Board Visibility and Archiving

**User Story:** As a Supervisor, Manager, or Admin, I want to control board visibility and archive boards and cards, so that guests see only what is intended and finished work stays recoverable.

#### Acceptance Criteria

1. THE Backend SHALL store each Board's `visibility` as exactly `public` or `private`.
2. WHEN a Manager, an Admin, or a Supervisor who is the Board_Owner or a BoardMember sets a Board's visibility, THE Backend SHALL apply the change and record it in the Activity_Log (Decision A).
3. IF an authenticated Member, or a Supervisor who is neither owner nor BoardMember, attempts to set Board visibility, THEN THE Backend SHALL return HTTP 403, or HTTP 401 when no Token is present.
4. WHEN a Guest requests the Board list, THE Backend SHALL return only Boards where `visibility` is `public` and `deleted_at` is null.
5. IF a Guest requests a private Board, THEN THE Backend SHALL return HTTP 401 with an error Envelope.
6. WHEN a signed-in Member requests a private Board where the Member is neither the Board's owner, a BoardMember, a Manager, nor an Admin, THE Backend SHALL return HTTP 403 (Decision A).
7. WHEN a Guest requests a public Board, THE Backend SHALL return its Columns and Cards and omit `comments` and `activity_log`.
8. WHEN a Manager or Admin archives a Board, THE Backend SHALL set the Board's `archived_at` and allow the archive to be reversed (Decision 4).
9. IF an authenticated Member or Supervisor attempts to archive a Board, THEN THE Backend SHALL return HTTP 403, or HTTP 401 when no Token is present (Decision 4).
10. WHEN a Supervisor, Manager, or Admin with Board_Staff_Access archives a Card, THE Backend SHALL set the Card's `archived_at`.
11. IF a signed-in Supervisor who is neither the Board_Owner nor a BoardMember requests a private Board, THEN THE Backend SHALL return HTTP 403 (Decision A).
12. WHEN a signed-in user requests the Board list, THE Backend SHALL return the public non-deleted Boards plus the non-deleted Boards to which the user has Board_Access (Decision A).
