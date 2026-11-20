### Requirement 6: Categories

**User Story:** As a Supervisor, Manager, or Admin, I want to manage each board's own categories, so that viewers can filter cards by the kinds of work that board runs.

#### Acceptance Criteria

V10 changes: criterion 6 reworded (a Guest reads Categories only through the shared route). All other criteria are unchanged from V8.

6. WHEN a Guest requests `GET /api/shared/{token}/categories` with a valid Share_Token, THE Backend SHALL return that Board's Categories; a Guest request to `GET /api/boards/{board_id}/categories` SHALL return HTTP 401 (Decision K; reworded in V10).
