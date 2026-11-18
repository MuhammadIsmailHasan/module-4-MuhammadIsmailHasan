### Requirement 6: Categories

**User Story:** As a Supervisor, Manager, or Admin, I want to manage each board's own categories, so that viewers can filter cards by the kinds of work that board runs.

#### Acceptance Criteria

1. WHEN a Supervisor, Manager, or Admin creates a Category on a Board, THE Backend SHALL store the Category with the Board's id, a name, and a nullable color.
2. WHEN a Supervisor, Manager, or Admin renames or recolors a Category, THE Backend SHALL apply the change through `PATCH /api/categories/{id}`.
3. WHEN a Supervisor, Manager, or Admin deletes a Category, THE Backend SHALL remove it through `DELETE /api/categories/{id}`.
4. IF a Member or Guest attempts to create, edit, or delete a Category, THEN THE Backend SHALL return HTTP 403.
5. WHEN any user with access to a Board requests `GET /api/boards/{board_id}/categories`, THE Backend SHALL return that Board's Categories without a role check.
6. WHEN a Guest requests the Categories of a public Board, THE Backend SHALL return them.
7. THE Backend SHALL return only the Categories owned by the requested Board.
8. WHEN a Board row is removed from the database, THE Backend SHALL cascade-delete that Board's Categories.
9. THE Frontend SHALL render the Board's filter-row chips from the `GET /api/boards/{board_id}/categories` response and use no hard-coded chip list.
10. WHEN the viewer switches Boards, THE Frontend SHALL re-fetch and re-render the filter-row chips.
11. WHERE the viewer is a Supervisor, Manager, or Admin, THE Frontend SHALL show a Categories entry in the Sidebar that opens an add, rename, recolor, and delete screen scoped to the current Board.
