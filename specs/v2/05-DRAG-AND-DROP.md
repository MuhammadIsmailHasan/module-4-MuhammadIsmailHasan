### Requirement 5: Drag-and-Drop Card Movement

**User Story:** As a team member, I want to drag cards between columns, so that a card's new position persists after a page refresh.

#### Acceptance Criteria

1. WHEN a user drops a Card between two siblings with `order` values a and b, THE Backend SHALL set the moved Card's Float `order` to the average of a and b without rewriting sibling rows, except for the renumbering defined in criterion 11.
2. WHEN a user drops a Card, THE Frontend SHALL call `PATCH /api/cards/{id}/move` with the target Column and computed Float `order` on `dragend` and reconcile local state with the response.
3. WHEN a drag is in progress, THE Frontend SHALL insert a placeholder at the drop target and animate sibling Cards into place with a FLIP transform.
4. WHEN a Member with Board_Access moves a Card assigned to that Member, THE Backend SHALL apply the move (Decisions 2 and A).
5. IF a Member moves a Card whose `assignee_id` is not that Member, THEN THE Backend SHALL return HTTP 403 (Decision 2).
6. WHEN a Supervisor, Manager, or Admin with Board_Staff_Access to the Card's Board moves any Card on that Board, THE Backend SHALL apply the move (Decision A).
7. IF a request to move a Card carries no Token, THEN THE Backend SHALL return HTTP 401.
8. WHEN a Card move succeeds, THE Backend SHALL write exactly one Activity_Log row with action `card.moved` and the source and target Column in the same transaction.
9. WHEN a page is refreshed after a successful move, THE Frontend SHALL render the Card in the moved position.
10. WHEN a user drops a Card at the first position of a Column, THE Backend SHALL set the Card's `order` to `min_order - 1`, WHEN at the last position, to `max_order + 1`, and WHEN into an empty Column, to 1.0.
11. IF the gap between two adjacent `order` values in a Column falls below 1e-6, THEN THE Backend SHALL renumber that whole Column as 1.0, 2.0, ... in the same transaction as the move.
12. IF the target Column's `board_id` does not match the Card's current `board_id`, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR`.
