### Requirement 3: Boards and Columns

**User Story:** As a Manager or Admin, I want to create boards and assign them to supervisors, so that each project has an owner and a consistent workflow.

#### Acceptance Criteria

1. WHEN a Manager or Admin creates a Board, THE Backend SHALL insert the Board and the five Default_Columns with `order` values 0 to 4 in that sequence, in a single transaction.
2. WHEN a Manager or Admin assigns a Board to a Supervisor, THE Backend SHALL store that Supervisor's id in the Board's nullable `owner_id`.
3. IF a Member or Supervisor attempts to create a Board, THEN THE Backend SHALL return HTTP 403.
4. WHEN a Supervisor, Manager, or Admin creates a Column on a Board, THE Backend SHALL append the Column with the next `order` value.
5. IF a Member or Guest attempts to create a Column, THEN THE Backend SHALL return HTTP 403.
6. WHEN a Manager or Admin soft-deletes a Board, THE Backend SHALL set the Board's `deleted_at` and exclude the Board from default queries.
7. IF a Member, Supervisor, or Guest attempts to soft-delete a Board, THEN THE Backend SHALL return HTTP 403.
8. THE Backend SHALL never hard-delete a row from the Board table.
9. THE Frontend SHALL list the Boards the viewer may see in the Sidebar and use that list as the Board switcher.
10. WHILE a Board is open, THE Frontend SHALL render the Board's Columns and Cards in the main area.
