# Visibility, V12 changes

Board visibility is removed (Decision Y, Requirement 22). Requirement 11 criteria 1 to 3, 6, 11, 12, and 13 are superseded; criteria 4, 5, and 7 to 10 stand. Archive and soft-delete of Boards and Cards are unchanged.

1. THE Backend SHALL store each Board's `visibility` as exactly `public` or `private`. **(Superseded in V12 by Requirement 22: Boards have no visibility; kept for history.)**
2. WHEN a Manager, an Admin, or a Supervisor who is the Board_Owner or a BoardMember sets a Board's visibility, THE Backend SHALL apply the change and record it in the Activity_Log (Decision A). **(Superseded in V12 by Requirement 22: Boards have no visibility; kept for history.)**
3. IF an authenticated Member, or a Supervisor who is neither owner nor BoardMember, attempts to set Board visibility, THEN THE Backend SHALL return HTTP 403, or HTTP 401 when no Token is present. **(Superseded in V12 by Requirement 22: Boards have no visibility; kept for history.)**
4. IF a visitor without a Token requests the Board list, THEN THE Backend SHALL return HTTP 401 with an error Envelope (Decision K; reverses V2 to V9, which returned the public Boards to a Guest; breaking).
5. IF a Guest requests any Board by id, public or private, through a route other than a shared route, THEN THE Backend SHALL return HTTP 401 with an error Envelope (Decision K; widened in V10 from private Boards to every Board). (V12: every Board is private.)
6. WHEN a signed-in Member requests a private Board where the Member is neither the Board's owner, a BoardMember, a Manager, nor an Admin, THE Backend SHALL return HTTP 403 (Decision A). **(Superseded in V12 by Requirement 22: Boards have no visibility; kept for history.)**
7. THE Backend SHALL return a Board's Columns and Cards to a Guest only through the shared routes of Requirement 18, and those responses SHALL omit `comments`, `activity`, and `activity_log` (Decision K; reworded in V10).
8. WHEN a Manager or Admin archives a Board, THE Backend SHALL set the Board's `archived_at` and allow the archive to be reversed (Decision 4).
9. IF an authenticated Member or Supervisor attempts to archive a Board, THEN THE Backend SHALL return HTTP 403, or HTTP 401 when no Token is present (Decision 4).
10. WHEN a Supervisor, Manager, or Admin with Board_Staff_Access archives a Card, THE Backend SHALL set the Card's `archived_at`.
11. IF a signed-in Supervisor who is neither the Board_Owner nor a BoardMember requests a private Board, THEN THE Backend SHALL return HTTP 403 (Decision A). **(Superseded in V12 by Requirement 22: Boards have no visibility; kept for history.)**
12. WHEN a signed-in user requests the Board list, THE Backend SHALL return the public non-deleted Boards plus the non-deleted Boards to which the user has Board_Access (Decision A). **(Superseded in V12 by Requirement 22: Boards have no visibility; kept for history.)**
13. THE Backend SHALL let every signed-in user, a Member included, read a public Board and its Columns, Cards, and Categories; only a Guest loses public browsing (Decisions A and K, restated in V10). **(Superseded in V12 by Requirement 22: Boards have no visibility; kept for history.)**
