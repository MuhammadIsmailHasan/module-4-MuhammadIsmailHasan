### Requirement 12: Search and Filter

**User Story:** As a user viewing a board, I want to search and filter its cards, so that I can find work quickly.

#### Acceptance Criteria
**Round 3 within V10 (Decisions U to W):** criterion 6 now points to Decision W for Open Question 13.

V10 changes: criteria 6 and 7 reworded (Guests search only through the shared route). All other criteria are unchanged from V2.

6. WHEN a Guest calls `GET /api/shared/{token}/cards` with `search` or `filter[...]`, THE Backend SHALL apply them as criteria 1 and 2 do and return Card data only, with no Comment or Activity_Log fields (Decision K; reworded in V10; Open Question 13 is resolved by Decision W).
7. IF a signed-in user without Board_Access calls the Cards endpoint of a private Board, THEN THE Backend SHALL return HTTP 403, and IF a Guest calls `GET /api/boards/{id}/cards` of any Board, THEN THE Backend SHALL return HTTP 401 (Decisions A and K).
