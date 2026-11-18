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
