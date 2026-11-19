### Requirement 10: Analytics

**User Story:** As a Supervisor or Manager, I want pre-aggregated board analytics, so that I can judge progress without opening every board.

#### Acceptance Criteria

1. WHEN a Supervisor requests `GET /api/boards/{id}/analytics` for a Board whose `owner_id` is that Supervisor, THE Backend SHALL return an Analytics_Summary (Decision 1).
2. IF a Supervisor requests analytics for a Board whose `owner_id` is not that Supervisor, including a Board where that Supervisor is a BoardMember, THEN THE Backend SHALL return HTTP 403.
3. WHEN a Manager requests analytics for any Board, THE Backend SHALL return an Analytics_Summary.
4. IF an authenticated Member or Admin requests analytics, THEN THE Backend SHALL return HTTP 403, and IF no Token is present, THEN THE Backend SHALL return HTTP 401 (Decision B, intentional).
5. THE Backend SHALL return Analytics_Summary payloads of counts, deltas, and overdue totals, such as `{ "status": true, "message": "OK", "data": { "done": 12, "in_progress": 4, "overdue": 2 } }`, counting an Overdue_Card as a Card whose `end_date` is before today, whose Column is not `Done`, and which is not soft-deleted, and never a raw dump of every Card.
6. WHEN a Manager requests cross-board analytics, THE Backend SHALL return one Analytics_Summary per Board in a single pre-aggregated response.
7. THE Backend SHALL grant a Supervisor analytics access only through Board ownership and never through BoardMember (Decision A).
