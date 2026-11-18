### Requirement 12: Search and Filter

**User Story:** As a user viewing a board, I want to search and filter its cards, so that I can find work quickly.

#### Acceptance Criteria

1. WHEN a user calls `GET /api/boards/{id}/cards` with `search=<text>`, THE Backend SHALL return only Cards on that Board whose text matches the search value.
2. WHEN a user calls `GET /api/boards/{id}/cards` with `filter[priority]`, `filter[assignee]`, or `filter[category]`, THE Backend SHALL return only Cards matching every supplied filter.
3. THE Backend SHALL exclude Soft_Deleted Cards from search and filter results.
4. IF a filter field is not supported, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR`.
5. WHEN a user selects a Category chip, THE Frontend SHALL request the Board's Cards with the matching category filter.
6. WHEN a Guest searches a public Board, THE Backend SHALL return Card data only and no Comment or Activity_Log fields.
