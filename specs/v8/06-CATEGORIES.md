### Requirement 6: Categories

**User Story:** As a Supervisor, Manager, or Admin, I want to manage each board's own categories, so that viewers can filter cards by the kinds of work that board runs.

#### Acceptance Criteria

1. WHEN a Manager, an Admin, or a Supervisor with Board_Staff_Access creates a Category on a Board, THE Backend SHALL store the Category with the Board's id, a name, and a nullable color (Decision A).
2. WHEN a Manager, an Admin, or a Supervisor with Board_Staff_Access renames or recolors a Category, THE Backend SHALL apply the change through `PATCH /api/categories/{id}`.
3. WHEN a Manager, an Admin, or a Supervisor with Board_Staff_Access deletes a Category, THE Backend SHALL remove it through `DELETE /api/categories/{id}`.
4. IF an authenticated Member, or a Supervisor without Board_Staff_Access, attempts to create, edit, or delete a Category, THEN THE Backend SHALL return HTTP 403, or HTTP 401 when no Token is present.
5. WHEN a user with Board_Access to a Board requests `GET /api/boards/{board_id}/categories`, THE Backend SHALL return that Board's Categories without a role check (Decision A).
6. WHEN a Guest requests the Categories of a public Board, THE Backend SHALL return them.
7. THE Backend SHALL return only the Categories owned by the requested Board.
8. WHEN a Board is soft-deleted, THE Backend SHALL keep that Board's Categories stored and make them unreachable.
9. THE Frontend SHALL render the Board's filter-row chips from the `GET /api/boards/{board_id}/categories` response and use no hard-coded chip list.
10. WHEN the viewer switches Boards, THE Frontend SHALL re-fetch and re-render the filter-row chips.
11. WHERE the viewer is a Supervisor, Manager, or Admin, THE Frontend SHALL show a Categories entry in the Sidebar that opens an add, rename, recolor, and delete screen scoped to the current Board.
12. IF a Category create or rename uses a name that already exists on the same Board when compared case-insensitively, THEN THE Backend SHALL return HTTP 409 with the code `CONFLICT`.
13. THE Frontend SHALL draw each Category filter chip with a border, using the brand colour for the border of the active chip (Decision I).
14. THE Frontend SHALL display every Category name in lowercase (board Cards, filter chips, the Card modal, the Categories screen) through styling only, keeping the stored name as entered (Decision I).
