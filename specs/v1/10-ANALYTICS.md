### Requirement 10: Analytics

**User Story:** As a Supervisor or Manager, I want pre-aggregated board analytics, so that I can judge progress without opening every board.

#### Acceptance Criteria

1. WHEN a Supervisor requests `GET /api/boards/{id}/analytics` for a Board whose `owner_id` is that Supervisor, THE Backend SHALL return an Analytics_Summary.
2. IF a Supervisor requests analytics for a Board whose `owner_id` is not that Supervisor, THEN THE Backend SHALL return HTTP 403.
3. WHEN a Manager requests analytics for any Board, THE Backend SHALL return an Analytics_Summary.
4. IF a Member, Admin, or Guest requests analytics, THEN THE Backend SHALL return HTTP 403, or HTTP 401 when no Token is present.
5. THE Backend SHALL return Analytics_Summary payloads of counts, deltas, and overdue totals, such as `{ "data": { "done": 12, "in_progress": 4, "overdue": 2 } }`, and never a raw dump of every Card.
6. WHEN a Manager requests cross-board analytics, THE Backend SHALL return one Analytics_Summary per Board in a single pre-aggregated response.
