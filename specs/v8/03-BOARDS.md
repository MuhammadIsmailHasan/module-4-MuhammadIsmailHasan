### Requirement 3: Boards and Columns

**User Story:** As a Manager or Admin, I want to create boards and assign them to supervisors, so that each project has an owner and a consistent workflow.

#### Acceptance Criteria

1. WHEN a Manager or Admin creates a Board, THE Backend SHALL insert the Board and the five Default_Columns with `order` values 0 to 4 in that sequence, in a single transaction.
2. WHEN a Manager or Admin assigns a Board to a Supervisor, THE Backend SHALL store that Supervisor's id in the Board's nullable `owner_id` (Decision 1).
3. IF an authenticated Member or Supervisor attempts to create a Board, THEN THE Backend SHALL return HTTP 403, or HTTP 401 when no Token is present.
4. WHEN a Manager or Admin, or a Supervisor who is the Board_Owner or a BoardMember of the Board, creates a Column on that Board, THE Backend SHALL append the Column with the next `order` value (Decision A).
5. IF an authenticated Member, or a Supervisor without Board_Access as owner or BoardMember, attempts to create a Column, THEN THE Backend SHALL return HTTP 403, or HTTP 401 when no Token is present (Decision A).
6. WHEN a Manager or Admin soft-deletes a Board, THE Backend SHALL set the Board's `deleted_at` and exclude the Board from default queries (Decision 4).
7. IF an authenticated Member or Supervisor attempts to soft-delete a Board, THEN THE Backend SHALL return HTTP 403, or HTTP 401 when no Token is present (Decision 4).
8. THE Backend SHALL never hard-delete a row from the Board table.
9. THE Frontend SHALL list the Boards the viewer may see in the Sidebar and use that list as the Board switcher.
10. WHILE a Board is open, THE Frontend SHALL render the Board's Columns and Cards in the main area.
11. WHEN the Board_Owner, a Manager, or an Admin adds a user to a Board through `POST /api/boards/{id}/members`, THE Backend SHALL create a BoardMember for that Board and user (Decision A).
12. IF an authenticated user who is not the Board_Owner, a Manager, or an Admin attempts to add or remove a BoardMember, THEN THE Backend SHALL return HTTP 403, or HTTP 401 when no Token is present (Decision A).
13. IF a BoardMember add targets a user who is already a BoardMember of that Board, THEN THE Backend SHALL return HTTP 409 with an error Envelope (Decision A).
14. WHEN the Board_Owner, a Manager, or an Admin removes a BoardMember through `DELETE /api/boards/{id}/members/{user_id}`, THE Backend SHALL delete that BoardMember record (Decision A).
15. WHEN a BoardMember is added or removed, THE Backend SHALL write one Activity_Log row for the change in the same transaction (Decision A).
16. WHEN a Manager or Admin reassigns a Board's `owner_id` to a user who has the supervisor role, THE Backend SHALL store the new `owner_id` (Decision 1).
17. IF a Board `owner_id` reassignment names a user who does not have the supervisor role, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR`.
18. WHEN a Manager or Admin clears a Board's `owner_id`, THE Backend SHALL set `owner_id` to null.
19. WHEN a Board's `owner_id` is reassigned or cleared, THE Backend SHALL write one Activity_Log row in the same transaction.
20. THE Frontend SHALL show each Board's visibility in the Sidebar Boards list and in the Board header as an icon with an accessible label and tooltip: a closed lock for `private` and an open lock for `public` (Decision I).
21. THE Frontend SHALL wrap a long Board name onto further lines in the Sidebar and in the Board header instead of cutting it off, and SHALL show the full name as a tooltip in the Sidebar (Decision I).
22. WHEN a signed-in user opens Home, THE Frontend SHALL show a page at `/boards` that lists every Board the viewer may see, each with its visibility icon, and SHALL make Home the first Sidebar entry and the default destination after sign-in (Decision I).
23. THE Frontend SHALL show the Board header in two rows: the first holds the visibility icon and Board name on the left and the Inbox bell and the signed-in user on the right; the second holds three bordered sections, progress ("12 of 18 done", the percent, and a thin bar) on the left, the Category filter chips in the middle as one strip that scrolls sideways with left and right arrow buttons shown only when more chips are hidden, and the search field on the right; the header SHALL have no Add Member button and no settings icon, and below 960 pixels the search field SHALL collapse to an icon that opens the search in a modal (Decision I).
24. THE Frontend SHALL keep one Team members section in the Sidebar, listing the Board's members, with no separate Members navigation entry; WHERE the viewer is the Board_Owner, a Manager, or an Admin, the section heading SHALL carry an add button that opens a member search (a popover, or a modal when the viewport is too narrow) and each member SHALL carry a remove button that asks for confirmation (Decision I).
25. WHEN the Board_Owner, a Manager, or an Admin requests `GET /api/boards/{id}/candidates?search=<text>`, THE Backend SHALL return at most 20 users who are not yet BoardMembers of that Board, matched case-insensitively on name or login_identifier and ordered by name, each with only `id` and `full_name`; IF another signed-in user calls it, THEN THE Backend SHALL return HTTP 403, and with no Token HTTP 401 (Decision I).
26. WHEN a user requests `GET /api/boards`, THE Backend SHALL include on each Board `card_count` (Cards not soft-deleted and not archived), `done_count` (of those, Cards in the `Done` Column), `overdue_count` (of those, Overdue_Cards), and `member_count` (BoardMembers), computed in a fixed number of queries whatever the number of Boards (Decision I).
27. THE Backend SHALL store a nullable Board `description` of at most 500 characters, accepted on `POST /api/boards` and `PATCH /api/boards/{id}` under the same role rules as the Board name, returned on every Board response, and SHALL return HTTP 400 with the code `VALIDATION_ERROR` for a longer value (Decision I).
28. THE Frontend SHALL offer an optional Description field in the new-board modal, sending it only when it is not empty (Decision I).
29. THE Frontend SHALL show each Board on Home as a plain bordered tile (no cover band or image) with the visibility icon and name, up to two lines of the description, a progress bar with the percent from `done_count` and `card_count`, the counts of Cards, Overdue_Cards, and members, and up to three member avatars followed by "+N" (Decision I).
