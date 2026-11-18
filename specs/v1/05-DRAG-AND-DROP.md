### Requirement 5: Drag-and-Drop Card Movement

**User Story:** As a team member, I want to drag cards between columns, so that a card's new position persists after a page refresh.

#### Acceptance Criteria

1. WHEN a user drops a Card between two siblings with `order` values a and b, THE Backend SHALL set the moved Card's Float `order` to the average of a and b without rewriting sibling rows.
2. WHEN a user drops a Card, THE Frontend SHALL call `PATCH /api/cards/{id}/move` with the target Column and computed Float `order` on `dragend` and reconcile local state with the response.
3. WHEN a drag is in progress, THE Frontend SHALL insert a placeholder at the drop target and animate sibling Cards into place with a FLIP transform.
4. WHEN a Member moves a Card assigned to that Member, THE Backend SHALL apply the move.
5. IF a Member moves a Card whose `assignee_id` is not that Member, THEN THE Backend SHALL return HTTP 403.
6. WHEN a Supervisor, Manager, or Admin moves any Card on a visible Board, THE Backend SHALL apply the move.
7. IF a Guest attempts to move a Card, THEN THE Backend SHALL return HTTP 401 when no Token is present.
8. WHEN a Card move succeeds, THE Backend SHALL write exactly one Activity_Log row with action `card.moved` and the source and target Column in the same transaction.
9. WHEN a page is refreshed after a successful move, THE Frontend SHALL render the Card in the moved position.
