### Requirement 11: Board Visibility and Archiving

**User Story:** As a Supervisor, Manager, or Admin, I want to control board visibility and archive boards and cards, so that guests see only what the owner shares through a link and finished work stays recoverable.

#### Acceptance Criteria

V10 changes: criteria 4, 5, and 7 reworded (no Guest browsing; breaking), criterion 13 added (every signed-in user reads public Boards, Decision A restated). Criterion 12 is shown for context and is unchanged. All other criteria are unchanged from V2.

4. IF a visitor without a Token requests the Board list, THEN THE Backend SHALL return HTTP 401 with an error Envelope (Decision K; reverses V2 to V9, which returned the public Boards to a Guest; breaking).
5. IF a Guest requests any Board by id, public or private, through a route other than a shared route, THEN THE Backend SHALL return HTTP 401 with an error Envelope (Decision K; widened in V10 from private Boards to every Board).
7. THE Backend SHALL return a Board's Columns and Cards to a Guest only through the shared routes of Requirement 18, and those responses SHALL omit `comments`, `activity`, and `activity_log` (Decision K; reworded in V10).
12. WHEN a signed-in user requests the Board list, THE Backend SHALL return the public non-deleted Boards plus the non-deleted Boards to which the user has Board_Access (Decision A).
13. THE Backend SHALL let every signed-in user, a Member included, read a public Board and its Columns, Cards, and Categories; only a Guest loses public browsing (Decisions A and K, restated in V10).
